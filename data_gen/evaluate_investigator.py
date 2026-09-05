import sys
import json
import os

from datetime import datetime, timezone
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


RESULTS_FILE = "evaluation_results.jsonl"


def log_result(record):
    """Append one result immediately so progress survives interruptions."""

    record["logged_at"] = datetime.now(timezone.utc).isoformat()

    with open(RESULTS_FILE, "a") as f:
        f.write(json.dumps(record) + "\n")
def load_results():
    """Load all previously logged evaluation results."""

    if not os.path.exists(RESULTS_FILE):
        return []

    results = []

    with open(RESULTS_FILE, "r") as f:
        for line in f:
            line = line.strip()

            if not line:
                continue

            try:
                results.append(json.loads(line))
            except json.JSONDecodeError:
                continue

    return results
def summarize_results():
    results = load_results()

    completed = [
        r for r in results
        if r.get("status") not in {
            "quota_exhausted",
            "skipped",
            "error"
        }
        and "passed" in r
    ]

    passed = sum(
        1 for r in completed
        if r["passed"]
    )

    failed = sum(
        1 for r in completed
        if not r["passed"]
    )

    return {
        "total": len(completed),
        "passed": passed,
        "failed": failed
    }

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

    passed = predicted == incident_type

    return {
        "expected": incident_type,
        "predicted": predicted,
        "confidence": ai_result.get("confidence"),
        "incident_id": incident.incident_id,
        "passed": passed
    }

def main():

    NUM_TRIALS = 5 # will increase it when quota is not exhausted

    incident_types = [
        "duplicate_payment",
        "missing_refund"
    ]

    total_tests = 0
    passed_tests = 0
    failed_tests = 0

    print("\n========================================")
    print("FINTRACE AI EVALUATION")
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

                    log_result({
                        "incident_type": incident_type,
                        "trial": trial,
                        "status": "skipped"
                    })

                    continue

                total_tests += 1

                expected = result["expected"]
                predicted = result["predicted"]
                passed = result["passed"]

                if passed:

                    passed_tests += 1

                else:

                    failed_tests += 1

                print(
                    f"  Trial {trial}: "
                    f"{'PASS' if passed else 'FAIL'} "
                    f"| predicted={predicted} "
                    f"| confidence={result['confidence']}"
                )

                log_result({
                    "incident_type": incident_type,
                    "expected": expected,
                    "predicted": predicted,
                    "confidence": result["confidence"],
                    "incident_id": result["incident_id"],
                    "passed": passed
                })

            except Exception as e:

                if "RESOURCE_EXHAUSTED" in str(e):

                    log_result({
                        "incident_type": incident_type,
                        "trial": trial,
                        "status": "quota_exhausted"
                    })

                    print(
                        f"\n  Quota exhausted — stopping."
                        f" Progress saved in {RESULTS_FILE}."
                    )

                    return

                print(
                    f"  Trial {trial}: ERROR | {e}"
                )

                log_result({
                    "incident_type": incident_type,
                    "trial": trial,
                    "status": "error",
                    "error": str(e)
                })

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

    # ---------------------------------------------------------
    # Cumulative metrics across all evaluation runs
    # ---------------------------------------------------------

    cumulative = summarize_results()

    print("\n========================================")
    print("        CUMULATIVE RESULTS")
    print("========================================")
    print(f"Total completed tests : {cumulative['total']}")
    print(f"Passed                : {cumulative['passed']}")
    print(f"Failed                : {cumulative['failed']}")

    if cumulative["total"] > 0:
        accuracy = (
            cumulative["passed"] / cumulative["total"]
        ) * 100
        print(f"Accuracy              : {accuracy:.2f}%")

    print("========================================\n")

if __name__ == "__main__":
      main()