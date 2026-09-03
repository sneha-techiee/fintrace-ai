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


def run_single_evaluation(incident_type):

    # ---------------------------------------------------------
    # 1. Generate financial data
    # ---------------------------------------------------------

    merchants = generate_merchants()

    payments = generate_payments(
        merchants,
        20
    )

    # ---------------------------------------------------------
    # Guarantee one valid completed payment for evaluation
    # ---------------------------------------------------------

    payments[0].status = "completed"

    period_start = datetime(2026, 6, 1)

    period_end = datetime(
        2026, 6, 30,
        23, 59, 59
    )

    refunds = generate_refunds(
        payments,
        10,
        period_end
    )

    # ---------------------------------------------------------
    # 2. Guarantee a valid refund scenario for evaluation
    # ---------------------------------------------------------

    if incident_type == "missing_refund":

        completed_payment = payments[0]


        test_refund = Refund(
            refund_id="test_refund_1",
            payment_id=completed_payment.payment_id,
            merchant_id=completed_payment.merchant_id,
            amount=Decimal("100.00"),
            status="completed",
            currency=completed_payment.currency,
            timestamp=datetime(2026, 6, 15)
        )

        refunds.append(test_refund)

    # ---------------------------------------------------------
    # 3. Generate ledger entries
    # ---------------------------------------------------------

    ledger_entries = generate_ledger_entries(
        payments,
        refunds
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
    # 5. Generate clean dashboard
    # ---------------------------------------------------------

    dashboard_metrics = generate_dashboard_metrics(
        ledger_truth,
        merchants,
        period_start,
        period_end
    )

    # ---------------------------------------------------------
    # 6. Inject known incident
    # ---------------------------------------------------------

    simulator = INCIDENT_SIMULATORS.get(
        incident_type
    )

    if simulator is None:
        raise ValueError(
            f"Unknown incident type: {incident_type}"
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
        return None

    # ---------------------------------------------------------
    # 7. Detect incident
    # ---------------------------------------------------------

    incidents = detect_incidents(
        ledger_truth,
        faulty_dashboard_metrics,
        injected_incident_type
    )

    if not incidents:
        return None

    incident = incidents[0]

    # ---------------------------------------------------------
    # 8. Gather evidence
    # ---------------------------------------------------------

    evidence = gather_evidence(
        incident,
        payments,
        ledger_entries,
        period_start,
        period_end
    )

    # ---------------------------------------------------------
    # 9. Structure evidence
    # ---------------------------------------------------------

    structured_evidence = build_investigation_evidence(
        evidence
    )

    # ---------------------------------------------------------
    # 10. Ask AI
    # ---------------------------------------------------------

    ai_result = investigate_with_ai(
        structured_evidence
    )

    # ---------------------------------------------------------
    # 11. Return evaluation result
    # ---------------------------------------------------------

    predicted = ai_result.get(
        "root_cause_category"
    )

    return {
        "expected": incident_type,
        "predicted": predicted,
        "confidence": ai_result.get("confidence"),
        "incident_id": incident.incident_id
    }


def main():

    NUM_TRIALS = 1

    incident_types = [
        "duplicate_payment",
        "missing_refund"
    ]

    total_tests = 0
    passed_tests = 0
    failed_tests = 0

    print("\n========================================")
    print("       FINTRACE AI EVALUATION")
    print("========================================")

    for incident_type in incident_types:

        print(
            f"\nTesting: {incident_type}"
        )

        for trial in range(1, NUM_TRIALS + 1):

            try:

                result = run_single_evaluation(
                    incident_type
                )

                if result is None:

                    print(
                        f"  Trial {trial}: SKIPPED "
                        f"(scenario could not be generated)"
                    )

                    continue

                total_tests += 1

                expected = result["expected"]
                predicted = result["predicted"]

                if predicted == expected:

                    passed_tests += 1

                    print(
                        f"  Trial {trial}: PASS "
                        f"| predicted={predicted} "
                        f"| confidence={result['confidence']}"
                    )

                else:

                    failed_tests += 1

                    print(
                        f"  Trial {trial}: FAIL "
                        f"| expected={expected} "
                        f"| predicted={predicted} "
                        f"| confidence={result['confidence']}"
                    )

            except Exception as e:

                print(
                    f"  Trial {trial}: ERROR | {e}"
                )

    # ---------------------------------------------------------
    # Final metrics
    # ---------------------------------------------------------

    print("\n========================================")
    print("              RESULTS")
    print("========================================")

    print(f"Total tests : {total_tests}")
    print(f"Passed      : {passed_tests}")
    print(f"Failed      : {failed_tests}")

    if total_tests > 0:

        accuracy = (
            passed_tests / total_tests
        ) * 100

        print(
            f"Accuracy    : {accuracy:.2f}%"
        )

    print("========================================\n")


if __name__ == "__main__":
    main()