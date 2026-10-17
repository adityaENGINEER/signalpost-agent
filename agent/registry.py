import time
import requests
from typing import Dict, Any, Optional, List

BRREG_BASE_URL = "https://data.brreg.no/enhetsregisteret/api"

class NorwegianRegistryClient:
    """
    Client for Brønnøysundregistrene (The Brønnøysund Register Centre)
    Official public Norwegian government registry.
    Free, open access, zero token cost.
    """
    def __init__(self, timeout: int = 20, max_retries: int = 3):
        self.session = requests.Session()
        self.session.headers.update({
            "Accept": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9,no;q=0.8"
        })
        self.timeout = timeout
        self.max_retries = max_retries

    def fetch_company(self, org_number: str) -> Optional[Dict[str, Any]]:
        """
        Fetch company record by 9-digit organisasjonsnummer with automatic retry
        """
        clean_org = str(org_number).strip().replace(" ", "")
        url = f"{BRREG_BASE_URL}/enheter/{clean_org}"
        for attempt in range(self.max_retries):
            try:
                resp = self.session.get(url, timeout=self.timeout)
                if resp.status_code == 200:
                    return resp.json()
                elif resp.status_code == 404:
                    return None
            except Exception as e:
                if attempt == self.max_retries - 1:
                    print(f"[Warning] Failed to fetch {clean_org} after {self.max_retries} attempts: {e}")
                time.sleep(1.5 * (attempt + 1))
        return None

    def fetch_batch_companies(self, page: int = 0, size: int = 100) -> List[Dict[str, Any]]:
        """
        Fetch a page of active companies from the public registry with retry
        """
        url = f"{BRREG_BASE_URL}/enheter"
        params = {
            "page": page,
            "size": min(size, 100),
            "konkurs": "false"
        }
        for attempt in range(self.max_retries):
            try:
                resp = self.session.get(url, params=params, timeout=self.timeout)
                if resp.status_code == 200:
                    data = resp.json()
                    return data.get("_embedded", {}).get("enheter", [])
            except Exception as e:
                time.sleep(1.5 * (attempt + 1))
        return []
