from typing import Dict, Any, List
import json
import os

def get_analytics_metrics(store_path: str = "data/profiles_store.json") -> Dict[str, Any]:
    if not os.path.exists(store_path):
        return {"total": 0, "industries": {}, "types": {}, "statuses": {}, "avg_quality": 0}

    with open(store_path, "r", encoding="utf-8") as f:
        store: Dict[str, Any] = json.load(f)

    total = len(store)
    if total == 0:
        return {"total": 0, "industries": {}, "types": {}, "statuses": {}, "avg_quality": 0}

    industries: Dict[str, int] = {}
    types: Dict[str, int] = {}
    active_count = 0
    bankrupt_count = 0
    total_quality = 0

    from .intelligence import calculate_data_quality

    for org, p in store.items():
        # Industry
        ind = p.get("industry_description") or "Undisclosed / Other"
        # truncate long industry names for charts
        if len(ind) > 32:
            ind = ind[:30] + "..."
        industries[ind] = industries.get(ind, 0) + 1

        # Type
        t = p.get("org_type_description") or p.get("org_type") or "Other Entity"
        if len(t) > 28:
            t = t[:26] + "..."
        types[t] = types.get(t, 0) + 1

        # Status
        if p.get("is_bankrupt"):
            bankrupt_count += 1
        elif p.get("is_active"):
            active_count += 1

        # Quality
        q = calculate_data_quality(p)
        total_quality += q["score"]

    # Sort top 7 industries
    sorted_ind = sorted(industries.items(), key=lambda x: x[1], reverse=True)[:7]
    sorted_types = sorted(types.items(), key=lambda x: x[1], reverse=True)[:6]

    return {
        "total_records": total,
        "active_records": active_count,
        "bankrupt_records": bankrupt_count,
        "avg_quality_score": round(total_quality / total, 1) if total else 0,
        "top_industries": dict(sorted_ind),
        "top_types": dict(sorted_types),
        "dataset_name": "Official Brønnøysundregistrene Norwegian Dataset (1,000+ Enheter)"
    }
