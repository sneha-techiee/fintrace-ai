# The job of this file is:
# Run the complete FinTrace investigation pipeline.
#
# Data generation
#     ↓
# Fault injection
#     ↓
# Incident detection
#     ↓
# Evidence collection
#     ↓
# AI investigation
#     ↓
# Investigation report


from data_gen.generate_merchants import generate_merchants
from data_gen.generate_payments import generate_payments
from data_gen.generate_refunds import generate_refunds
from data_gen.generate_ledger import generate_ledger_entries

from data_gen.calculate_ledger_truth import calculate_ledger_truth
from data_gen.generate_dashboard_metrics import generate_dashboard_metrics

from data_gen.simulate_duplicate_payment import simulate_duplicate_payment

from data_gen.detect_incidents import detect_incidents

from data_gen.lineage import gather_evidence

from data_gen.investigation_evidence import build_investigation_evidence
from data_gen.ai_investigator import investigate_with_ai
from data_gen.investigation_report import generate_investigation_report


if __name__ == "__main__":

    # ---------------------------------------------------------
    # 1. Generate financial data
    # ---------------------------------------------------------

    merchants = generate_merchants()

    payments = generate_payments(
        merchants,
        20
    )

    refunds = generate_refunds(
        payments,
        10
    )

    ledger_entries = generate_ledger_entries(
        payments,
        refunds
    )

    # ---------------------------------------------------------
    # 2. Select a merchant/payment for investigation
    # ---------------------------------------------------------

    target_payment = next(
        (
            payment
            for payment in payments
            if payment.status == "completed"
        ),
        None
    )

    if target_payment is None:
        raise RuntimeError(
            "No completed payment available for duplicate-payment simulation."
        )

    target_merchant_id = target_payment.merchant_id

    merchant_payments = [
        payment
        for payment in payments
        if payment.merchant_id == target_merchant_id
    ]

    if not merchant_payments:
        raise RuntimeError(
            "No payments found for the selected merchant."
        )

    # ---------------------------------------------------------
    # 3. Define investigation period
    # ---------------------------------------------------------

    period_start = min(
        payment.timestamp
        for payment in merchant_payments
    )

    period_end = max(
        payment.timestamp
        for payment in merchant_payments
    )

    # ---------------------------------------------------------
    # 4. Calculate clean ledger truth
    # ---------------------------------------------------------

    ledger_truth = calculate_ledger_truth(
        ledger_entries,
        period_start,
        period_end
    )

    # ---------------------------------------------------------
    # 5. Generate the clean dashboard
    # ---------------------------------------------------------

    dashboard_metrics = generate_dashboard_metrics(
    ledger_truth,
    merchants,
    period_start,
    period_end
)

    # ---------------------------------------------------------
    # 6. Inject a financial data problem
    # ---------------------------------------------------------

    result = simulate_duplicate_payment(
        dashboard_metrics,
        payments,
        ledger_entries,
        target_merchant_id,
        period_start,
        period_end
    )

    if result is None:
        raise RuntimeError(
            "Could not create a duplicate-payment scenario."
        )

    faulty_dashboard_metrics, incident_type = result

    # ---------------------------------------------------------
    # 7. Detect the incident
    # ---------------------------------------------------------

    incidents = detect_incidents(
        ledger_truth,
        faulty_dashboard_metrics,
        incident_type
    )

    if not incidents:
        raise RuntimeError(
            "No financial incident was detected."
        )

    incident = incidents[0]

    # ---------------------------------------------------------
    # 8. Collect investigation evidence
    # ---------------------------------------------------------

    evidence = gather_evidence(
        incident,
        payments,
        ledger_entries,
        period_start,
        period_end
    )

    # ---------------------------------------------------------
    # 9. Structure evidence for the AI
    # ---------------------------------------------------------

    structured_evidence = build_investigation_evidence(
        evidence
    )

    # ---------------------------------------------------------
    # 10. Ask AI to investigate
    # ---------------------------------------------------------

    ai_result = investigate_with_ai(
        structured_evidence
    )

    # ---------------------------------------------------------
    # 11. Generate final investigation report
    # ---------------------------------------------------------

    report = generate_investigation_report(
        ai_result
    )

    # ---------------------------------------------------------
    # 12. Display the result
    # ---------------------------------------------------------

    print("\n=== FINTRACE AI INVESTIGATION ===")

    print("\nIncident:")
    print(f"  ID: {report['incident_id']}")
    print(f"  Merchant: {report['merchant_id']}")
    print(
        f"  Discrepancy: "
        f"{report['currency']} {report['discrepancy']}"
    )
    print(f"  Severity: {report['severity']}")

    print("\nRoot Cause:")
    print(f"  {report['root_cause']}")

    print("\nExplanation:")
    print(f"  {report['explanation']}")

    print("\nEvidence:")
    for item in report["evidence"]:
        print(f"  - {item}")

    print("\nConfidence:")
    print(f"  {report['confidence']}")