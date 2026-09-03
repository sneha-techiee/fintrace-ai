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

import sys

from data_gen.incident_registry import INCIDENT_SIMULATORS
from data_gen.generate_merchants import generate_merchants
from data_gen.generate_payments import generate_payments
from data_gen.generate_refunds import generate_refunds
from data_gen.generate_ledger import generate_ledger_entries
from data_gen.calculate_ledger_truth import calculate_ledger_truth
from data_gen.generate_dashboard_metrics import generate_dashboard_metrics

from data_gen.detect_incidents import detect_incidents
from data_gen.lineage import gather_evidence
from data_gen.investigation_evidence import build_investigation_evidence
from data_gen.ai_investigator import investigate_with_ai
from data_gen.investigation_report import generate_investigation_report


if __name__ == "__main__":

    if len(sys.argv) < 2:
        raise ValueError(
            "Please provide an incident type. "
            "Example: python -m data_gen.run_investigation missing_refund"
        )

    incident_type = sys.argv[1]

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

    if incident_type == "missing_refund":

        target_refund = next(
            (
                refund
                for refund in refunds
                if refund.status == "completed"
            ),
            None
        )

        if target_refund is None:
            raise RuntimeError(
                "No completed refund available for missing-refund simulation."
            )

        target_merchant_id = target_refund.merchant_id

    elif incident_type == "duplicate_payment":

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

    else:
        raise ValueError(
            f"Unsupported incident type: {incident_type}"
        )

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

    if incident_type == "missing_refund":

        period_end = max(
            target_refund.timestamp,
            max(payment.timestamp for payment in merchant_payments)
        )

    else:

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

    simulator = INCIDENT_SIMULATORS.get(incident_type)

    if simulator is None:
        raise ValueError(
            f"Unknown incident type: {incident_type}. "
            f"Available types: {list(INCIDENT_SIMULATORS.keys())}"
        )

    if incident_type == "duplicate_payment":

        result = simulator(
            dashboard_metrics,
            payments,
            ledger_entries,
            target_merchant_id,
            period_start,
            period_end
        )

    else:

        result = simulator(
            dashboard_metrics,
            refunds,
            ledger_entries,
            target_merchant_id,
            period_start,
            period_end
        )

    if result is None:
        raise RuntimeError(
            f"Could not create a {incident_type} scenario."
        )

    faulty_dashboard_metrics, injected_incident_type = result

    if injected_incident_type is None:
        raise RuntimeError(
            f"Simulator could not create a {incident_type} scenario."
        )

    # ---------------------------------------------------------
    # 7. Detect the incident
    # ---------------------------------------------------------

    incidents = detect_incidents(
        ledger_truth,
        faulty_dashboard_metrics,
        injected_incident_type
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