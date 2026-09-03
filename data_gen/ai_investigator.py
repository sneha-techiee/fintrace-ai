# The job of this file:
# Use investigation evidence to explain an incident.
#
# Evidence
#    ↓
# AI Investigator
#    ↓
# Root cause explanation
#    ↓
# Recommended action
#
# IMPORTANT:
# This file does NOT retrieve evidence.
# This file does NOT calculate the discrepancy.
# This file does NOT decide the incident type.
# It only reasons over the evidence that it receives.

import os
import json

from dotenv import load_dotenv
from google import genai

load_dotenv()


def investigate_with_ai(evidence):
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is not set. "
            "Make sure your Gemini API key is present in the .env file."
        )

    client = genai.Client(api_key=api_key)

    # Incident type is metadata about how the test scenario was generated.
    # It must NOT be treated as evidence of the root cause.
    incident_metadata = evidence["incident"].copy()
    incident_metadata.pop("incident_type", None)

    investigation_evidence = {
        "incident": incident_metadata,
        "payments": evidence["payments"],
        "ledger_entries": evidence["ledger_entries"]
    }

    prompt = f"""
You are an AI financial incident investigator.

Your job is to independently investigate a financial discrepancy
using ONLY the financial evidence provided below.

Your goal is to determine the most likely root cause of the discrepancy.

IMPORTANT RULES:

1. Use ONLY the evidence provided below.

2. Do NOT invent transactions, payments, refunds, ledger entries,
   pipeline runs, schemas, or other facts.

3. The original incident_type is intentionally NOT provided.
   You must NOT rely on a predefined incident category.

4. Determine the root cause independently from the financial records.

5. Compare expected_revenue, actual_revenue, and discrepancy.

6. Examine individual payment records and ledger entries.

7. Look for relationships between:
   - payment amounts
   - ledger amounts
   - payment status
   - refunds
   - duplicate records
   - missing records
   - mismatched amounts
   - repeated identifiers

8. If a discrepancy exactly matches a particular financial record,
   explicitly explain that relationship.

9. Identify the specific records that support your conclusion.

10. Do NOT assume that a matching amount automatically proves a root cause.
    Explain why the available evidence supports the conclusion.

11. If the evidence is insufficient or ambiguous, explicitly say so.

12. Do not claim certainty when the evidence does not justify it.

13. The evidence field must contain concrete observations from
    the supplied financial records.

14. Return ONLY valid JSON.

The expected JSON structure is:

{{
    "incident_id": "string",
    "merchant_id": "string",
    "discrepancy": "string",
    "currency": "string",
    "severity": "string",
    "root_cause": "string",
    "explanation": "string",
    "evidence": ["string"],
    "confidence": "string"
}}

FINANCIAL INVESTIGATION EVIDENCE:

{json.dumps(investigation_evidence, indent=2)}
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config={
            "response_mime_type": "application/json"
        }
    )

    if response.text is None:
      raise RuntimeError("Gemini returned an empty response.")

    result = json.loads(response.text)

    return result