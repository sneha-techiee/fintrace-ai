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
from datetime import datetime
from decimal import Decimal

from data_gen.models import Refund
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
    # ---------------------------------------------------------
    # 2. Define investigation period
    # ---------------------------------------------------------

    period_start = datetime(2026, 6, 1)

    period_end = datetime(
        2026, 6, 30,
        23, 59, 59
    )

     # ---------------------------------------------------------
# Guarantee valid records for deterministic demo scenarios
# ---------------------------------------------------------

# Ensure at least one completed payment exists.
# This does NOT tell the AI what the root cause is.
    payments[0].status = "completed"

    refunds = generate_refunds(
    payments,
    10,
    period_end
)

# For the missing_refund scenario, guarantee one completed
# refund exists before the ledger and ground truth are created.
    if incident_type == "missing_refund":

      guaranteed_refund = Refund(
        refund_id="demo_refund_1",
        payment_id=payments[0].payment_id,
        merchant_id=payments[0].merchant_id,
        amount=Decimal("10.00"),
        status="completed",
        currency=payments[0].currency,
        timestamp=datetime(2026, 6, 15)
    )

      refunds.append(guaranteed_refund)

    ledger_entries = generate_ledger_entries(
    payments,
    refunds
)
    


    # ---------------------------------------------------------
    # 3. Calculate clean ledger truth
    # ---------------------------------------------------------

    ledger_truth = calculate_ledger_truth(
        ledger_entries,
        period_start,
        period_end
    )

    # ---------------------------------------------------------
    # 4. Generate the clean dashboard
    # ---------------------------------------------------------

    dashboard_metrics = generate_dashboard_metrics(
        ledger_truth,
        merchants,
        period_start,
        period_end
    )

    # ---------------------------------------------------------
    # 5. Inject a financial data problem
    # ---------------------------------------------------------

    simulator = INCIDENT_SIMULATORS.get(incident_type)

    if simulator is None:
        raise ValueError(
            f"Unknown incident type: {incident_type}. "
            f"Available types: {list(INCIDENT_SIMULATORS.keys())}"
        )

    faulty_dashboard_metrics, injected_incident_type = simulator(
        dashboard_metrics,
        merchants,
        payments,
        refunds,
        ledger_entries,
        period_start,
        period_end
    )

    

    if injected_incident_type is None:
        raise RuntimeError(
            f"Simulator could not create a {incident_type} scenario."
        )

    # ---------------------------------------------------------
    # 6. Detect the incident
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
    # 7. Collect investigation evidence
    # ---------------------------------------------------------

    evidence = gather_evidence(
        incident,
        payments,
        ledger_entries,
        period_start,
        period_end
    )

    # ---------------------------------------------------------
    # 8. Structure evidence for the AI
    # ---------------------------------------------------------

    structured_evidence = build_investigation_evidence(
        evidence
    )

    # ---------------------------------------------------------
    # 9. Ask AI to investigate
    # ---------------------------------------------------------

    ai_result = investigate_with_ai(
        structured_evidence
    )

    # ---------------------------------------------------------
    # 10. Generate final investigation report
    # ---------------------------------------------------------

    report = generate_investigation_report(
        ai_result
    )

    # ---------------------------------------------------------
    # 11. Display the result
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