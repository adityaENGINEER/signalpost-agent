from agent.validator import normalize_org_number, format_org_number

cases = [
    ("923 456 789", True, "923456789"),
    ("923456789", True, "923456789"),
    ("923  456  789", True, "923456789"),
    ("923 456 78", False, None),
    ("9234567890", False, None),
    ("92345AB89", False, None),
]

all_passed = True
print("=== TESTING NORWEGIAN ORG NUMBER NORMALIZATION & VALIDATION ===")
for inp, expected_valid, expected_norm in cases:
    valid, norm, err = normalize_org_number(inp)
    passed = (valid == expected_valid) and (norm == expected_norm)
    if not passed:
        all_passed = False
    status_str = "PASS" if passed else "FAIL"
    print(f"[{status_str}] Input: {repr(inp):<16} -> valid={valid:<5} norm={repr(norm):<12} error={repr(err)}")

assert all_passed, "Some test cases failed!"
print("\n[ALL 6/6 VALIDATION TEST CASES PASSED SUCCESSFULLY]")
