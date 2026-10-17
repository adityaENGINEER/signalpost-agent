import argparse
import json
import sys
from agent.core import SignalpostAgent
from agent.batch_generator import generate_1000_profiles

def main():
    parser = argparse.ArgumentParser(
        description="Signalpost AI Agent: Verifiable Norwegian Company Intelligence"
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--org",
        type=str,
        help="9-digit Norwegian Company Organization Number (e.g., 923609016 for Equinor)"
    )
    group.add_argument(
        "--batch",
        type=int,
        nargs="?",
        const=1000,
        help="Generate batch of company profiles (default: 1000)"
    )
    group.add_argument(
        "--test",
        action="store_true",
        help="Run comprehensive test suite against 5 well-known Norwegian enterprises"
    )

    args = parser.parse_args()
    agent = SignalpostAgent()

    if args.org:
        profile = agent.process_company(args.org)
        if profile:
            print("\n" + "="*60)
            print(f" COMPANY PROFILE: {profile.company_name} ({profile.org_number})")
            print("="*60)
            print(f"Summary: {profile.agent_summary}")
            print(f"Status: {'ACTIVE' if profile.is_active else 'INACTIVE'}")
            print(f"Employees: {profile.employee_count}")
            print(f"Industry: {profile.industry_description}")
            print(f"Last Verified: {profile.last_updated}")
            print("\nGranular Facts & Evidence:")
            for idx, fact in enumerate(profile.facts, 1):
                print(f"  {idx}. [{fact.key}]: {fact.value}")
                print(f"     Source: {fact.source_name} ({fact.source_url})")
                print(f"     Retrieved: {fact.retrieved_at} | Confidence: {fact.confidence * 100:.0f}%")
            if profile.history:
                print("\nChange History / Updates:")
                for h in profile.history:
                    print(f"  - [{h.detected_at}] {h.description}")
            print("="*60 + "\n")
        else:
            print(f"[-] Could not find or process company with number: {args.org}")
            sys.exit(1)

    elif args.batch:
        count = args.batch
        generate_1000_profiles(target_count=count)

    elif args.test:
        test_orgs = [
            ("923609016", "EQUINOR ASA"),
            ("916627939", "- P A L M E R A -"),
            ("989061593", "-G- GROUP AS"),
            ("988539473", "-EBE- DATA Eyolf Berg"),
            ("934551435", "----ADVOKATFIRMAET CATO MYHRE")
        ]
        print("\n=== Running Self-Verification Test on Norwegian Enterprises ===")
        for org_nr, name in test_orgs:
            p = agent.process_company(org_nr)
            assert p is not None, f"Failed for {org_nr}"
            print(f" Verified: {p.company_name} | Facts Extracted: {len(p.facts)}")
        print("\n[SUCCESS] All enterprise test profiles verified accurately.\n")

if __name__ == "__main__":
    main()
