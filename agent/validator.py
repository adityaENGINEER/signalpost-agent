import re
from typing import Optional, Tuple

def normalize_org_number(raw_input: Optional[str]) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Validates and normalizes Norwegian organization numbers.
    Rules:
    - Norwegian organization numbers contain exactly 9 digits.
    - Spaces must never count as digits. Remove all whitespace before validation.
    - Accepts both unspaced '923456789' and spaced '923 456 789' or multiple spaces '923  456  789'.
    - Rejects letters, punctuation, and other invalid characters.
    - Rejects numbers shorter or longer than 9 digits.
    
    Returns:
    (is_valid, normalized_9_digit, error_message)
    """
    if not raw_input:
        return False, None, "Please enter a valid 9-digit Norwegian organization number."

    # 1. Ignore all whitespace
    stripped = re.sub(r"\s+", "", str(raw_input))

    # 2. Check if it contains invalid non-digit characters
    if not stripped.isdigit():
        return False, None, "Please enter a valid 9-digit Norwegian organization number."

    # 3. Check exact length of 9 digits
    if len(stripped) != 9:
        return False, None, "Please enter a valid 9-digit Norwegian organization number."

    return True, stripped, None

def format_org_number(normalized: str) -> str:
    """
    Formats a 9-digit Norwegian organization number into the canonical readable format:
    'XXX XXX XXX'
    """
    if len(normalized) == 9 and normalized.isdigit():
        return f"{normalized[0:3]} {normalized[3:6]} {normalized[6:9]}"
    return normalized
