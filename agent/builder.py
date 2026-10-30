import re 
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from .models import CompanyProfile, FactWithEvidence, ChangeRecord

class ProfileBuilder:
    """
    Transforms official registry raw payloads into verified company profiles with
    granular evidence links, timestamps, and reasoning logs.
    """
    
    @staticmethod
    def extract_facts(raw_data: Dict[str, Any]) -> List[FactWithEvidence]:
        facts: List[FactWithEvidence] = []
        org_nr = raw_data.get("organisasjonsnummer", "")
        source_url = f"https://data.brreg.no/enhetsregisteret/api/enheter/{org_nr}"
        portal_url = f"https://virksomhet.brreg.no/nb/oppslag/enheter/{org_nr}"
        now_iso = datetime.now(timezone.utc).isoformat()
        
        # 1. Legal Name
        if "navn" in raw_data:
            facts.append(FactWithEvidence(
                key="legal_name",
                value=raw_data["navn"],
                source_name="Brønnøysundregistrene (Enhetsregisteret)",
                source_url=portal_url,
                retrieved_at=now_iso,
                confidence=1.0,
                explanation="Official registered entity name as recorded in the Central Coordinating Register for Legal Entities."
            ))
            
        # 2. Organization Number
        if "organisasjonsnummer" in raw_data:
            facts.append(FactWithEvidence(
                key="org_number",
                value=raw_data["organisasjonsnummer"],
                source_name="Brønnøysundregistrene (Enhetsregisteret)",
                source_url=source_url,
                retrieved_at=now_iso,
                confidence=1.0,
                explanation="Unique 9-digit official Norwegian legal entity identifier."
            ))
            
        # 3. Organization Form
        org_form = raw_data.get("organisasjonsform", {})
        if org_form:
            code = org_form.get("kode", "")
            desc = org_form.get("beskrivelse", "")
            facts.append(FactWithEvidence(
                key="legal_form",
                value=f"{desc} ({code})",
                source_name="Brønnøysundregistrene (Enhetsregisteret)",
                source_url=portal_url,
                retrieved_at=now_iso,
                confidence=1.0,
                explanation=f"Corporate entity structure type: {desc}."
            ))

        # 4. Registration Date
        reg_date = raw_data.get("registreringsdatoEnhetsregisteret")
        if reg_date:
            facts.append(FactWithEvidence(
                key="registration_date",
                value=reg_date,
                source_name="Brønnøysundregistrene (Enhetsregisteret)",
                source_url=portal_url,
                retrieved_at=now_iso,
                confidence=1.0,
                explanation="Official date of registration in the Norwegian legal entity register."
            ))

        # 5. Industry / NACE Code
        naering = raw_data.get("naeringskode1", {})
        if naering:
            code = naering.get("kode", "")
            desc = naering.get("beskrivelse", "")
            facts.append(FactWithEvidence(
                key="industry_classification",
                value=f"{code} - {desc}",
                source_name="Brønnøysundregistrene (SSB Standard Industrial Classification)",
                source_url=portal_url,
                retrieved_at=now_iso,
                confidence=1.0,
                explanation=f"Primary NACE activity classification: {desc}."
            ))

        # 6. Employee Count
        if "antallAnsatte" in raw_data:
            facts.append(FactWithEvidence(
                key="employee_count",
                value=raw_data["antallAnsatte"],
                source_name="NAV / Brønnøysundregistrene Aa-registeret",
                source_url=portal_url,
                retrieved_at=now_iso,
                confidence=1.0,
                explanation="Number of reported employees registered in the official Aa-register."
            ))

        # 7. Physical / Business Address
        b_addr = raw_data.get("forretningsadresse") or raw_data.get("beliggenhetsadresse")
        if b_addr:
            address_str = ", ".join(filter(None, [
                ", ".join(b_addr.get("adresse", [])),
                b_addr.get("postnummer"),
                b_addr.get("poststed"),
                b_addr.get("kommune"),
                b_addr.get("land")
            ]))
            facts.append(FactWithEvidence(
                key="business_address",
                value=address_str,
                source_name="Brønnøysundregistrene (Enhetsregisteret)",
                source_url=portal_url,
                retrieved_at=now_iso,
                confidence=1.0,
                explanation="Physical headquarters/registered office location."
            ))

        # 8. Insolvency & Bankruptcy Status
        is_konkurs = raw_data.get("konkurs", False)
        is_under_avvikling = raw_data.get("underAvvikling", False)
        status_str = "Bankrupt" if is_konkurs else ("In Liquidation" if is_under_avvikling else "Active / In Good Standing")
        facts.append(FactWithEvidence(
            key="operating_status",
            value=status_str,
            source_name="Brønnøysundregistrene Konkursregisteret",
            source_url=portal_url,
            retrieved_at=now_iso,
            confidence=1.0,
            explanation="Legal solvency and operating condition per Norwegian register."
        ))

        # 9. Website if registered
        hjemmeside = raw_data.get("hjemmeside")
        if hjemmeside:
            facts.append(FactWithEvidence(
                key="official_website",
                value=hjemmeside,
                source_name="Brønnøysundregistrene (Entity Self-Reported)",
                source_url=portal_url,
                retrieved_at=now_iso,
                confidence=0.95,
                explanation="Official website registered by the company with the authority."
            ))

        return facts

    @classmethod
    def build_profile(cls, raw_data: Dict[str, Any], existing_profile: Optional[CompanyProfile] = None) -> CompanyProfile:
        facts = cls.extract_facts(raw_data)
        org_nr = raw_data.get("organisasjonsnummer", "")
        name = raw_data.get("navn", "Unknown")
        org_form = raw_data.get("organisasjonsform", {})
        naering = raw_data.get("naeringskode1", {})
        b_addr = raw_data.get("forretningsadresse") or raw_data.get("beliggenhetsadresse")
        p_addr = raw_data.get("postadresse")
        
        is_bankrupt = raw_data.get("konkurs", False)
        is_active = not is_bankrupt and not raw_data.get("underAvvikling", False)

        # Generate readable Agent summary & explanation
        emp_text = f"employing {raw_data.get('antallAnsatte', 0)} registered personnel" if raw_data.get('antallAnsatte') is not None else "with unlisted headcount"
        industry_text = f"specializing in {naering.get('beskrivelse', 'general enterprise')}" if naering else "in undisclosed sector"
        summary = (
            f"{name} (Org Nr: {org_nr}) is a Norwegian {org_form.get('beskrivelse', 'entity')} "
            f"{industry_text}, {emp_text}. "
            f"Headquartered in {b_addr.get('poststed', 'Norway') if b_addr else 'Norway'}, "
            f"operating status is currently {('ACTIVE' if is_active else 'INACTIVE/LIQUIDATION')}."
        )

        history = existing_profile.history if existing_profile else []

        # If previous profile exists, check for changes
        if existing_profile:
            now_iso = datetime.now(timezone.utc).isoformat()
            if existing_profile.employee_count != raw_data.get("antallAnsatte"):
                history.append(ChangeRecord(
                    key="employee_count",
                    old_value=existing_profile.employee_count,
                    new_value=raw_data.get("antallAnsatte"),
                    detected_at=now_iso,
                    description=f"Employee count changed from {existing_profile.employee_count} to {raw_data.get('antallAnsatte')}."
                ))
            if existing_profile.company_name != name:
                history.append(ChangeRecord(
                    key="company_name",
                    old_value=existing_profile.company_name,
                    new_value=name,
                    detected_at=now_iso,
                    description=f"Company name updated from '{existing_profile.company_name}' to '{name}'."
                ))

        return CompanyProfile(
            org_number=org_nr,
            company_name=name,
            is_active=is_active,
            is_bankrupt=is_bankrupt,
            registration_date=raw_data.get("registreringsdatoEnhetsregisteret"),
            org_type=org_form.get("kode"),
            org_type_description=org_form.get("beskrivelse"),
            industry_code=naering.get("kode") if naering else None,
            industry_description=naering.get("beskrivelse") if naering else None,
            employee_count=raw_data.get("antallAnsatte"),
            business_address=b_addr,
            postal_address=p_addr,
            website=raw_data.get("hjemmeside"),
            facts=facts,
            agent_summary=summary,
            last_updated=datetime.now(timezone.utc).isoformat(),
            history=history
        )
