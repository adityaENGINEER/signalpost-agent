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
    page = 0
    size = 100

    pbar = tqdm(total=target_count, desc="Processing Profiles", unit="company")

    while len(profiles) < target_count:
        batch = registry.fetch_batch_companies(page=page, size=size)
        if not batch:
            print(f"[!] No more records at page {page}, retrying...")
            time.sleep(2)
            page += 1
            if page > 50:
                break
            continue

        for item in batch:
            org_nr = item.get("organisasjonsnummer")
            if not org_nr or org_nr in seen_orgs:
                continue
            seen_orgs.add(org_nr)

            # Build and verify profile
            profile = ProfileBuilder.build_profile(item)
            profiles.append(profile.model_dump())
            agent.save_to_store(profile)
            pbar.update(1)

            if len(profiles) >= target_count:
                break

        page += 1
        time.sleep(0.1) # Gentle rate-limiting

    pbar.close()

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(profiles, f, indent=2, ensure_ascii=False)

    print(f"\n[SUCCESS] Generated {len(profiles)} company profiles saved to: {output_file}")
    return profiles

if __name__ == "__main__":
    generate_1000_profiles()
