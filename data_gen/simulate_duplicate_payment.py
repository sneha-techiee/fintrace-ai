# The job of this file is:
# Create a duplicate-payment incident by making the dashboard
# count one payment twice.
#
# Clean dashboard
#       ↓
# duplicate one payment
#       ↓
# INCORRECT dashboard
#
# This file creates the incident.
# It does NOT investigate or explain the cause.

from data_gen.models import DashboardMetric
def find_duplicable_payment(
    payments,
    ledger_entries,
    target_merchant_id,
    period_start,
    period_end
):

    ledger_payment_ids = {
        entry.payment_id
        for entry in ledger_entries
        if entry.entry_type == "payment"
    }

    for payment in payments:

        if (
            payment.merchant_id == target_merchant_id
            and payment.status == "completed"
            and payment.payment_id in ledger_payment_ids
            and period_start <= payment.timestamp <= period_end
        ):
            return payment

    return None

def simulate_duplicate_payment(
    dashboard_metrics,
    payments,
    ledger_entries,
    target_merchant_id,
    period_start,
    period_end
):

    faulty_dashboard_metrics = []

    selected_payment = find_duplicable_payment(
    payments,
    ledger_entries,
    target_merchant_id,
    period_start,
    period_end
)

    if selected_payment is None:
        return dashboard_metrics, None

    for dashboard_metric in dashboard_metrics:

        if dashboard_metric.merchant_id == target_merchant_id:

            # Make the dashboard count this payment one extra time.
            faulty_revenue = (
                dashboard_metric.revenue
                + selected_payment.amount
            )

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

    print(
        f"Selected payment: {selected_payment.merchant_id} | "
        f"{selected_payment.currency} "
        f"{selected_payment.amount} | "
        f"Payment: {selected_payment.payment_id}"
    )

    return faulty_dashboard_metrics, "duplicate_payment"