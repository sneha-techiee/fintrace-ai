# The job of this file is:
# Convert investigation evidence into a clear investigation report.
#
# Evidence
#    ↓
# Investigation Report
#
# The report explains:
# - What went wrong
# - Which merchant was affected
# - Which refund caused the discrepancy
# - Which payment was connected to that refund
# - What the likely root cause is

def generate_investigation_report(evidence):

    incident = evidence["incident"]
    refund = evidence["refund"]
    payment = evidence["payment"]

    report = {
        "incident_id": incident["incident_id"],
        "merchant_id": incident["merchant_id"],
        "discrepancy": incident["discrepancy"],
        "currency": incident["currency"],
        "severity": incident["severity"],

        "refund_amount": refund["amount"],
        "payment_id": payment["payment_id"],
        "original_payment_amount": payment["amount"],

        "root_cause": "Dashboard omitted a refund"
    }

    return report

