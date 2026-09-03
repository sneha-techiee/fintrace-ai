# The job of this file is:
# Convert the raw evidence collected by lineage.py
# into clean, structured evidence that can be given
# to the AI investigator.
#
# This file must NOT decide the root cause.
#
# Evidence
#    ↓
# Structured Investigation Evidence
#    ├── Incident details
#    ├── Payments
#    └── Ledger entries
#
# The AI investigator will examine this evidence
# and determine what actually happened.


def build_investigation_evidence(evidence):

    incident = evidence["incident"]

    structured_evidence = {
        "incident": {
            "incident_id": incident.incident_id,
            "merchant_id": incident.merchant_id,
            "incident_type": incident.incident_type,
            "expected_revenue": str(incident.expected_revenue),
            "actual_revenue": str(incident.actual_revenue),
            "discrepancy": str(incident.discrepancy),
            "currency": incident.currency,
            "severity": incident.severity
        },

        "payments": [
            {
                "payment_id": payment.payment_id,
                "merchant_id": payment.merchant_id,
                "amount": str(payment.amount),
                "currency": payment.currency,
                "status": payment.status,
                "timestamp": payment.timestamp.isoformat()
            }
            for payment in evidence["payments"]
        ],

        "ledger_entries": [
            {
                "entry_id": entry.entry_id,
                "payment_id": entry.payment_id,
                "merchant_id": entry.merchant_id,
                "entry_type": entry.entry_type,
                "amount": str(entry.amount),
                "currency": entry.currency,
                "timestamp": entry.timestamp.isoformat(),
                "direction": entry.direction
            }
            for entry in evidence["ledger_entries"]
        ]
    }

    return structured_evidence