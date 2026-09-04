import json
import os
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


PERIOD_START = datetime(2026, 6, 1)
PERIOD_END = datetime(2026, 6, 30, 23, 59, 59)

OUTPUT_FILE = "fintrace_data.json"

INCIDENT_TYPES = [
    "duplicate_payment",
    "missing_refund",
]


def run_scenario(incident_type):

    merchants = generate_merchants()

    payments = generate_payments(
        merchants,
        20
    )

    # Guarantee one valid completed payment
    # without revealing the incident type to the AI.
    payments[0].status = "completed"

    refunds = generate_refunds(
        payments,
        10,
        PERIOD_END
    )

    # Guarantee one valid refund for the
    # missing-refund scenario before truth is calculated.
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

    ledger_truth = calculate_ledger_truth(
        ledger_entries,
        PERIOD_START,
        PERIOD_END
    )

    dashboard_metrics = generate_dashboard_metrics(
        ledger_truth,
        merchants,
        PERIOD_START,
        PERIOD_END
    )

    simulator = INCIDENT_SIMULATORS.get(incident_type)

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
        PERIOD_START,
        PERIOD_END
    )

    if injected_incident_type is None:
        raise RuntimeError(
            f"Could not create {incident_type} scenario."
        )

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

    evidence = gather_evidence(
        incident,
        payments,
        ledger_entries,
        PERIOD_START,
        PERIOD_END
    )

    structured_evidence = build_investigation_evidence(
        evidence
    )

    ai_result = investigate_with_ai(
        structured_evidence
    )

    merchant_name = next(
        (
            merchant.name
            for merchant in merchants
            if merchant.merchant_id == incident.merchant_id
        ),
        incident.merchant_id
    )

    # ---------------------------------------------------------
    # Give every exported scenario a globally meaningful ID.
    #
    # detect_incidents() starts numbering from incident_1 for
    # every independent run, so we add the scenario identity here.
    # ---------------------------------------------------------

    exported_incident_id = (
        f"{incident_type}_{incident.incident_id}"
    )

    return {
        "incident_id": exported_incident_id,
        "merchant_id": incident.merchant_id,
        "merchant_name": merchant_name,
        "incident_type": incident.incident_type,
        "expected_revenue": str(incident.expected_revenue),
        "actual_revenue": str(incident.actual_revenue),
        "discrepancy": str(incident.discrepancy),
        "currency": incident.currency,
        "severity": incident.severity,
        "period": "June 2026",
        "evidence": structured_evidence,
        "ai_result": ai_result,
    }


def load_evaluation_summary():

    evaluation_file = "evaluation_results.jsonl"

    if not os.path.exists(evaluation_file):
        return {
            "total": 0,
            "passed": 0,
            "failed": 0,
            "accuracy": 0,
            "breakdown": []
        }

    results = []

    with open(evaluation_file, "r") as f:

        for line in f:

            line = line.strip()

            if not line:
                continue

            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue

            if (
                record.get("status") not in {
                    "quota_exhausted",
                    "skipped",
                    "error"
                }
                and "passed" in record
            ):
                results.append(record)

    total = len(results)

    passed = sum(
        1
        for record in results
        if record.get("passed") is True
    )

    failed = total - passed

    accuracy = (
        round((passed / total) * 100, 1)
        if total
        else 0
    )

    # ---------------------------------------------------------
    # Per-incident-type evaluation breakdown.
    #
    # This is derived entirely from actual evaluation logs.
    # No values are invented for the frontend.
    # ---------------------------------------------------------

    breakdown = []

    incident_types = sorted({
        record.get("incident_type")
        for record in results
        if record.get("incident_type")
    })

    for incident_type in incident_types:

        type_results = [
            record
            for record in results
            if record.get("incident_type") == incident_type
        ]

        type_total = len(type_results)

        type_passed = sum(
            1
            for record in type_results
            if record.get("passed") is True
        )

        type_accuracy = (
            round((type_passed / type_total) * 100, 1)
            if type_total
            else 0
        )

        breakdown.append({
            "incident_type": incident_type,
            "total": type_total,
            "passed": type_passed,
            "failed": type_total - type_passed,
            "accuracy": type_accuracy
        })

    return {
        "total": total,
        "passed": passed,
        "failed": failed,
        "accuracy": accuracy,
        "breakdown": breakdown
    }


def main():

    output = {
        "generated_at": datetime.now().isoformat(),
        "incidents": [],
        "evaluation": load_evaluation_summary()
    }

    for incident_type in INCIDENT_TYPES:

        try:

            incident = run_scenario(
                incident_type
            )

            output["incidents"].append(
                incident
            )

            print(
                f"✓ Generated {incident_type}: "
                f"{incident['incident_id']}"
            )

        except Exception as e:

            print(
                f"⚠ Could not generate {incident_type}: {e}"
            )

    with open(OUTPUT_FILE, "w") as f:

        json.dump(
            output,
            f,
            indent=2
        )

    print(
        f"\n✓ Frontend data written to {OUTPUT_FILE}"
    )


if __name__ == "__main__":
    main()