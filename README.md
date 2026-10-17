# Signalpost: Autonomous Norwegian Company Intelligence Agent

An agentic AI system designed for the **Builderr.ai Signalpost Competition** that autonomously searches, extracts, verifies, and continuously updates company intelligence for Norwegian entities using their 9-digit Organization Number (`organisasjonsnummer`).

---

## 🎯 Architecture & Winning Features

1. **Useful Information (35 pts):**
   - Directly links to **Brønnøysundregistrene (Enhetsregisteret & Aa-registeret)** — Norway's official national corporate repository.
   - Extracts complete legal names, entity types, NACE industry classification, exact employee headcounts, registered business and postal addresses, founding dates, and solvency/bankruptcy status.

2. **Strict Evidence Matching (30 pts):**
   - Every single fact contains verifiable attribution:
     - `key`: attribute identifier
     - `value`: factual data
     - `source_name`: official authority or registry
     - `source_url`: directly clickable public record URL
     - `retrieved_at`: UTC ISO-8601 timestamp
     - `confidence`: confidence score (1.0 for registry data)
     - `explanation`: human-readable justification of how the fact was derived

3. **Update & Change Detection (20 pts):**
   - Built-in incremental updater detects delta changes between runs (e.g. employee headcount updates, name modifications, or address adjustments) and maintains an audit history in `history[]`.

4. **Useful Explanations (10 pts):**
   - Natural language executive summary synthesizes all verified facts into an enterprise-ready briefing.

5. **One-Command Usability (5 pts):**
   - Single command execution for single entities, test suite, and 1,000+ profile batch generation.

---

## ⚡ Quickstart: One Command to Run It

### Setup
```bash
pip install -r requirements.txt
```

### 1. Research a Single Norwegian Company
```bash
python run.py --org 923609016
```
*(Example: 923609016 fetches Equinor ASA, Norway's largest energy corporation).*

### 2. Generate 1,000+ Company Profiles Dataset
```bash
python run.py --batch 1000
```
This will autonomously populate `output/norway_1000_profiles.json` with over 1,000 verified Norwegian corporate profiles.

### 3. Run Self-Verification Test
```bash
python run.py --test
```

---

## 📊 Model & API Details

- **Primary Source:** Brønnøysundregistrene Open API (`data.brreg.no/enhetsregisteret/api`)
- **Reasoning Architecture:** Local Deterministic & LLM-compatible profile builder (Pydantic Schema + Fact Verification Pipeline).
- **Network Resilience:** Auto-retry with exponential backoff and polite rate-limiting.

---

## 💰 Expected Run Costs

- **Brønnøysundregistrene Registry API:** **$0.00** (Free, open public government data).
- **Local Inference / Execution:** **$0.00** (Runs locally on CPU/GPU without cloud egress).
- **Total Expected Run Cost per 1,000 Profiles:** **$0.00 / Free**

---

## 📁 Repository Structure

```
├── agent/
│   ├── __init__.py
│   ├── models.py           # Pydantic fact & evidence data models
│   ├── registry.py         # Official Norwegian Brønnøysund API client
│   ├── builder.py          # Fact extraction, evidence linking & explainability
│   ├── core.py             # SignalpostAgent coordinator & storage
│   └── batch_generator.py  # 1,000+ profiles batch pipeline
├── data/
│   └── profiles_store.json # Persistent entity storage
├── output/
│   └── norway_1000_profiles.json # Final dataset of 1,000+ verified profiles
├── run.py                  # One-command CLI entrypoint
├── requirements.txt        # Minimal dependencies
└── README.md               # Submission documentation
```

---

## 🏆 Submission Metadata

- **Competition:** Builderr.ai - Signalpost: Build An Agent That Finds Company Information
- **Submission Email:** submit@builderr.ai
- **Dataset Target:** 1,000+ Norwegian Corporate Profiles
- **Author:** Aditya Upadhyay
