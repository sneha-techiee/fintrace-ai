# The job of this file is:
# Convert the investigation results into clean, structured evidence.
#
# Incident
#    ↓
# Evidence
#    ├── Incident details
#    ├── Refund details
#    └── Payment details
#
# This evidence will later be given to the AI agent
# so it can explain what happened and why.

def build_investigation_evidence(incident, refund, payment):

    evidence = {
        "incident": {
            "incident_id": incident.incident_id,
            "merchant_id": incident.merchant_id,
            "expected_revenue": str(incident.expected_revenue),
            "actual_revenue": str(incident.actual_revenue),
            "discrepancy": str(incident.discrepancy),
            "currency": incident.currency,
            "severity": incident.severity
        },

        "refund": {
            "payment_id": refund.payment_id,
            "merchant_id": refund.merchant_id,
            "amount": str(refund.amount),
            "currency": refund.currency,
            "timestamp": refund.timestamp.isoformat()
        },

        "payment": {
            "payment_id": payment.payment_id,
            "merchant_id": payment.merchant_id,
            "amount": str(payment.amount),
            "currency": payment.currency,
            "status": payment.status,
            "timestamp": payment.timestamp.isoformat()
        }
    }

    return evidence
       
        