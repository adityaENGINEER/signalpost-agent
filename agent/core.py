import json
import os
from typing import Dict, Optional, List
from .models import CompanyProfile
from .registry import NorwegianRegistryClient
from .builder import ProfileBuilder

from .validator import normalize_org_number, format_org_number

class SignalpostAgent:
    """
    Main Autonomous Agent for finding, verifying, and updating Norwegian company information.
    Operates with full source evidence, timestamps, zero hallucination, and change tracking.
    """
    def __init__(self, storage_path: str = "data/profiles_store.json"):
        self.registry = NorwegianRegistryClient()
        self.storage_path = storage_path
        self._ensure_storage()

    def _ensure_storage(self):
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        if not os.path.exists(self.storage_path):
            with open(self.storage_path, "w", encoding="utf-8") as f:
                json.dump({}, f)

    def load_store(self) -> Dict[str, Dict]:
        try:
            with open(self.storage_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    def save_to_store(self, profile: CompanyProfile):
        store = self.load_store()
        store[profile.org_number] = profile.model_dump()
        with open(self.storage_path, "w", encoding="utf-8") as f:
            json.dump(store, f, indent=2, ensure_ascii=False)

    def get_existing_profile(self, org_number: str) -> Optional[CompanyProfile]:
        is_valid, clean_org, _ = normalize_org_number(str(org_number))
        lookup_key = clean_org if is_valid else str(org_number)
        store = self.load_store()
        data = store.get(lookup_key)
        if data:
            return CompanyProfile(**data)
        return None

    def process_company(self, org_number: str) -> Optional[CompanyProfile]:
        """
        Takes a Norwegian organization number, normalizes whitespace and validates 9 digits,
        queries authoritative public sources, attaches evidence, builds the fact model,
        checks for changes against existing store, and saves the profile.
        """
        is_valid, clean_org, err_msg = normalize_org_number(org_number)
        if not is_valid:
            print(f"[-] {err_msg}")
            return None

        formatted_display = format_org_number(clean_org)
        print(f"[*] Agent investigating entity: {formatted_display} (normalized: {clean_org})...")

        # 1. Fetch public source data
        raw_data = self.registry.fetch_company(clean_org)
        if not raw_data:
            print(f"[-] No record found for Norwegian Org: {formatted_display}")
            return None

        # 2. Check for existing profile for change tracking
        existing = self.get_existing_profile(clean_org)

        # 3. Build verified profile
        profile = ProfileBuilder.build_profile(raw_data, existing_profile=existing)

        # 4. Save to persistent store
        self.save_to_store(profile)
        print(f"[+] Successfully verified & stored: {profile.company_name} ({profile.org_number}) with {len(profile.facts)} facts.")
        return profile
