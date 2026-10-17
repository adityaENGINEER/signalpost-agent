import os
import json
import time
from tqdm import tqdm
from typing import List, Dict
from .core import SignalpostAgent
from .registry import NorwegianRegistryClient
from .builder import ProfileBuilder

def generate_1000_profiles(output_file: str = "output/norway_1000_profiles.json", target_count: int = 1000):
    """
    Fetches real Norwegian companies from public register, processes each through the agent,
    and outputs at least 1,000 verified company profiles.
    """
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    registry = NorwegianRegistryClient()
    agent = SignalpostAgent()

    print(f"=== Starting Batch Generator for {target_count} Norwegian Company Profiles ===")
    
    profiles: List[Dict] = []
    seen_orgs = set()
    size = 100

    # Resume from existing profiles in store if available
    existing_store = agent.load_store()
    for k, v in existing_store.items():
        if k not in seen_orgs:
            seen_orgs.add(k)
            profiles.append(v)

    pbar = tqdm(total=target_count, desc="Processing Profiles", unit="company", initial=len(profiles))
    page = len(profiles) // size

    while len(profiles) < target_count:
        batch = registry.fetch_batch_companies(page=page, size=size)
        if not batch:
            print(f"[!] No more records at page {page}, retrying...")
            time.sleep(1)
            page += 1
            if page > 60:
                break
            continue

        new_batch_profiles = []
        for item in batch:
            org_nr = item.get("organisasjonsnummer")
            if not org_nr or org_nr in seen_orgs:
                continue
            seen_orgs.add(org_nr)

            profile = ProfileBuilder.build_profile(item)
            p_dict = profile.model_dump()
            profiles.append(p_dict)
            new_batch_profiles.append(profile)
            pbar.update(1)

            if len(profiles) >= target_count:
                break

        # Batch update store once per page (much faster)
        store = agent.load_store()
        for p in new_batch_profiles:
            store[p.org_number] = p.model_dump()
        with open(agent.storage_path, "w", encoding="utf-8") as f:
            json.dump(store, f, ensure_ascii=False)

        page += 1
        time.sleep(0.05)

    pbar.close()

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(profiles, f, indent=2, ensure_ascii=False)

    print(f"\n[SUCCESS] Generated {len(profiles)} company profiles saved to: {output_file}")
    return profiles

if __name__ == "__main__":
    generate_1000_profiles()
