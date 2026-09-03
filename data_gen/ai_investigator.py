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

You must determine the most likely root cause from the records.
The scenario type used to generate the test data is intentionally
hidden from you.

==================================================
CORE INVESTIGATION PRINCIPLE
==================================================

Do not simply find a record whose amount matches the discrepancy.

A matching amount is only a clue.

You must establish a logical relationship between:
    expected revenue
    actual revenue
    discrepancy
    individual financial records
    corresponding ledger entries

Your conclusion must explain WHY the records support the root cause.

==================================================
INVESTIGATION PROCESS
==================================================

Follow this reasoning process:

1. Identify the merchant and discrepancy.

2. Compare:
       expected_revenue
       actual_revenue
       discrepancy

3. Verify the arithmetic relationship:

       actual_revenue - expected_revenue = discrepancy

4. Examine the supplied payment records.

   For each relevant payment, consider:
   - payment_id
   - merchant_id
   - amount
   - status
   - timestamp

5. Examine the supplied ledger entries.

   For each relevant entry, consider:
   - entry_id
   - payment_id
   - entry_type
   - amount
   - direction
   - timestamp

6. Connect payments to their corresponding ledger entries.

7. Investigate whether the discrepancy can be explained by:

   A. Duplicate payment counting
      - A completed payment is already represented in the
        financial records.
      - The same payment amount explains the difference between
        expected and actual revenue.
      - Adding that payment amount to expected revenue produces
        the actual revenue.

   B. Missing refund deduction
      - A refund ledger entry exists for a completed refund.
      - The refund amount explains the discrepancy.
      - The actual revenue is higher than the expected revenue
        by exactly the refund amount.

   C. Missing or extra financial records
      - A relevant record exists in one part of the evidence
        but is absent or inconsistent in another.

   D. Amount mismatch
      - A payment or ledger record has inconsistent amounts.

   E. Other causes
      - Only use this when the supplied evidence supports it.

8. IMPORTANT FOR DUPLICATE DETECTION:

   Do NOT conclude "duplicate payment" merely because a payment
   amount equals the discrepancy.

   Strong evidence for duplicate counting exists when:

       expected_revenue + payment_amount = actual_revenue

   AND

       the payment is already represented by a corresponding
       payment ledger entry.

   If these conditions are satisfied, explicitly state that the
   payment appears to have been counted an additional time.

9. IMPORTANT FOR REFUND DETECTION:

   Do NOT conclude "missing refund" merely because a refund amount
   equals the discrepancy.

   Check whether:

       actual_revenue - refund_amount = expected_revenue

   and whether the refund has a corresponding ledger entry.

10. Consider alternative explanations before reaching a conclusion.

11. If the evidence is ambiguous, say that it is ambiguous.

12. If the evidence is insufficient, say that the root cause
    cannot be determined reliably.

==================================================
EVIDENCE REQUIREMENTS
==================================================

Every important conclusion must reference concrete records.

Whenever possible, include:
- payment IDs
- ledger entry IDs
- exact amounts
- relevant statuses
- explicit arithmetic relationships

For example:

"Payment pay_3 is a completed payment for INR 103.13."

"Ledger entry entry_1 records pay_3 as a payment credit
for INR 103.13."

"Expected revenue of INR 538.20 plus INR 103.13 equals
the actual revenue of INR 641.33."

Do not invent any record or value.

==================================================
CONFIDENCE
==================================================

Return confidence using ONLY:

- "high" — evidence strongly supports one explanation.
- "medium" — evidence supports the explanation but alternatives
  remain plausible.
- "low" — evidence is weak, incomplete, or ambiguous.

==================================================
IMPORTANT RULES
==================================================

1. Use ONLY the evidence provided below.

2. Do NOT invent transactions, payments, refunds, ledger entries,
   pipeline runs, schemas, or other facts.

3. The original incident_type is intentionally NOT provided.

4. Do NOT rely on a predefined incident category.

5. Do NOT assume a matching amount automatically proves a cause.

6. Perform the arithmetic explicitly when it helps establish
   the relationship.

7. Distinguish between:
   - a record matching the discrepancy
   - a record actually explaining the discrepancy

8. Do not claim certainty when the evidence does not justify it.

9. The evidence field must contain concrete observations from
   the supplied financial records.

10. Return ONLY valid JSON.

==================================================
EXPECTED JSON
==================================================

{{
    "incident_id": "string",
    "merchant_id": "string",
    "discrepancy": "string",
    "currency": "string",
    "severity": "string",
    "root_cause": "string",
    "explanation": "string",
    "evidence": ["string"],
    "confidence": "high | medium | low"
}}

==================================================
FINANCIAL INVESTIGATION EVIDENCE
==================================================

{json.dumps(investigation_evidence, indent=2)}
"""

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config={
                "response_mime_type": "application/json"
            }
        )
    except Exception as e:
        raise RuntimeError(
            f"AI investigation failed — Gemini API error: {e}"
        ) from e

    if not response.text:
        raise RuntimeError(
            "Gemini returned an empty response."
        )

    try:
        result = json.loads(response.text)
    except json.JSONDecodeError as e:
        raise RuntimeError(
            f"AI returned invalid JSON: {e}\n"
            f"Raw response: {response.text[:500]}"
        ) from e

    return result