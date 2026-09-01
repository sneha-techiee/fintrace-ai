# 1. Choose one merchant and make its dashboard revenue omit a refund amount.
#
# Clean dashboard revenue
#         ↓
# Add the refund amount back
#         ↓
# INCORRECT dashboard revenue

from data_gen.generate_merchants import generate_merchants
from data_gen.generate_payments import generate_payments
from data_gen.generate_refunds import generate_refunds
from data_gen.generate_ledger import generate_ledger_entries
from data_gen.calculate_ledger_truth import calculate_ledger_truth
from data_gen.generate_dashboard_metrics import generate_dashboard_metrics
from datetime import datetime
from data_gen.models import DashboardMetric
from data_gen.detect_incidents import detect_incidents


def simulate_missing_refund(
    dashboard_metrics,
    ledger_entries,
    target_merchant_id
):

    faulty_dashboard_metrics = []

    for dashboard_metric in dashboard_metrics:

        if dashboard_metric.merchant_id == target_merchant_id:

            refund_amount = None

            for entry in ledger_entries:

                if (
                    entry.merchant_id == target_merchant_id
                    and entry.entry_type == "refund"
                    and dashboard_metric.period_start
                    <= entry.timestamp
                    <= dashboard_metric.period_end
                ):
                    refund_amount = entry.amount

                    print(
                        f"Selected refund: {entry.merchant_id} | "
                        f"{entry.currency} {entry.amount} | "
                        f"Payment: {entry.payment_id}"
                    )

                    break

            if refund_amount is None:
                print("No suitable refund found. Try running again.")
                return faulty_dashboard_metrics, "missing_refund"

            faulty_revenue = dashboard_metric.revenue + refund_amount

            faulty_metric = DashboardMetric(
                merchant_id=dashboard_metric.merchant_id,
                revenue=faulty_revenue,
                currency=dashboard_metric.currency,
                period_start=dashboard_metric.period_start,
                period_end=dashboard_metric.period_end,
                pipeline_run_id=dashboard_metric.pipeline_run_id
            )

            faulty_dashboard_metrics.append(faulty_metric)

        else:
            faulty_dashboard_metrics.append(dashboard_metric)

    return faulty_dashboard_metrics, "missing_refund"


if __name__ == "__main__":

    merchants = generate_merchants(7)

    payments = generate_payments(
        merchants,
        17
    )

    refunds = generate_refunds(
        payments,
        10
    )

    ledger_entries = generate_ledger_entries(
        payments,
        refunds
    )

    period_start = datetime(
        2026,
        6,
        1
    )

    period_end = datetime(
        2026,
        6,
        30,
        23,
        59,
        59
    )

    ledger_truth = calculate_ledger_truth(
        ledger_entries,
        period_start,
        period_end
    )

    dashboard_metrics = generate_dashboard_metrics(
        ledger_truth,
        merchants,
        period_start,
        period_end
    )

    # Choose a merchant that actually has a refund
    target_merchant_id = None

    for entry in ledger_entries:

        if (
            entry.entry_type == "refund"
            and period_start <= entry.timestamp <= period_end
        ):
            target_merchant_id = entry.merchant_id
            break

    if target_merchant_id is None:
        print("No suitable refund found. Try running again.")
        exit()

    faulty_dashboard_metrics, incident_type = simulate_missing_refund(
        dashboard_metrics,
        ledger_entries,
        target_merchant_id
    )

    incidents = detect_incidents(
        ledger_truth,
        faulty_dashboard_metrics,
        incident_type
    )

    print("\n=== Clean Dashboard ===")

    for metric in dashboard_metrics:

        print(
            f"{metric.merchant_id} | "
            f"Revenue: {metric.currency} {metric.revenue}"
        )

    print("\n=== Faulty Dashboard ===")

    for metric in faulty_dashboard_metrics:

        print(
            f"{metric.merchant_id} | "
            f"Revenue: {metric.currency} {metric.revenue}"
        )

    print(
        f"\nIncident Merchant: {target_merchant_id}"
    )

    print("\n=== Detected Incidents ===")

    for incident in incidents:

        print(
            f"{incident.incident_id} | "
            f"Merchant: {incident.merchant_id} | "
            f"Type: {incident.incident_type} | "
            f"Expected: {incident.currency} "
            f"{incident.expected_revenue} | "
            f"Actual: {incident.currency} "
            f"{incident.actual_revenue} | "
            f"Difference: {incident.currency} "
            f"{incident.discrepancy} | "
            f"Severity: {incident.severity}"
        )