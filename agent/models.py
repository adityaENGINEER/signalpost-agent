from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class FactWithEvidence(BaseModel):
    key: str = Field(description="Name or identifier of the fact (e.g., legal_name, org_number, employee_count)")
    value: Any = Field(description="Value of the fact")
    source_name: str = Field(description="Source organization or public registry name")
    source_url: str = Field(description="Publicly verifiable URL where the fact was obtained")
    retrieved_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat(), description="ISO timestamp of data retrieval")
    confidence: float = Field(default=1.0, description="Confidence score from 0.0 to 1.0")
    explanation: Optional[str] = Field(default=None, description="Reasoning/derivation of this fact")

class ChangeRecord(BaseModel):
    key: str
    old_value: Any
    new_value: Any
    detected_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    description: str

class CompanyProfile(BaseModel):
    org_number: str
    company_name: str
    is_active: bool
    is_bankrupt: bool
    registration_date: Optional[str] = None
    org_type: Optional[str] = None
    org_type_description: Optional[str] = None
    industry_code: Optional[str] = None
    industry_description: Optional[str] = None
    employee_count: Optional[int] = None
    business_address: Optional[Dict[str, Any]] = None
    postal_address: Optional[Dict[str, Any]] = None
    website: Optional[str] = None
    facts: List[FactWithEvidence] = []
    agent_summary: str = ""
    last_updated: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    history: List[ChangeRecord] = []
