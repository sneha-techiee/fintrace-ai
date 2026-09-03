# The job of this file is:
# Create a faulty dashboard scenario where a refund is missing
# from the revenue calculation.
#
# IMPORTANT:
# This file only creates the faulty scenario.
# It does NOT detect the incident or decide the root cause.
#
# The AI investigator must determine what happened from the evidence.


def find_simulatable_refund(
    refunds,
    ledger_entries,
    period_start,
    period_end
):

    for refund in refunds:

        if (
            refund.status == "completed"
            and period_start <= refund.timestamp <= period_end
        ):

            refund_ledger_entry = next(
                (
                    entry
                    for entry in ledger_entries
                    if (
                        entry.merchant_id == refund.merchant_id
                        and entry.payment_id == refund.payment_id
                        and entry.entry_type == "refund"
                        and entry.amount == refund.amount
                    )
                ),
                None
            )

            if refund_ledger_entry is not None:
                return refund

    return None


def simulate_missing_refund(
    dashboard_metrics,
    merchants,
    payments,
    refunds,
    ledger_entries,
    period_start,
    period_end
):

    selected_refund = find_simulatable_refund(
        refunds,
        ledger_entries,
        period_start,
        period_end
    )

    if selected_refund is None:
        return dashboard_metrics, None

    target_merchant_id = selected_refund.merchant_id

    faulty_dashboard_metrics = []

    for metric in dashboard_metrics:

        if metric.merchant_id == target_merchant_id:

            # The refund should have reduced revenue,
            # but the faulty dashboard fails to deduct it.
            faulty_metric = type(metric)(
                merchant_id=metric.merchant_id,
                revenue=metric.revenue + selected_refund.amount,
                currency=metric.currency,
                period_start=metric.period_start,
                period_end=metric.period_end,
                pipeline_run_id=metric.pipeline_run_id
            )

            faulty_dashboard_metrics.append(faulty_metric)

        else:

            faulty_dashboard_metrics.append(metric)

    print(
        f"Selected refund: "
        f"{selected_refund.merchant_id} | "
        f"{selected_refund.currency} "
        f"{selected_refund.amount} | "
        f"Refund: {selected_refund.refund_id}"
    )

    return faulty_dashboard_metrics, "missing_refund"