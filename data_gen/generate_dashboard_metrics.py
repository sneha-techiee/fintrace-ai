from datetime import datetime
# from decimal import Decimal 
from data_gen.calculate_ledger_truth import calculate_ledger_truth
from data_gen.generate_merchants import generate_merchants
from data_gen.generate_payments import generate_payments
from data_gen.generate_refunds import generate_refunds
from data_gen.generate_ledger import generate_ledger_entries
from data_gen.models import DashboardMetric
def generate_dashboard_metrics(ledger_truth, merchants, period_start, period_end):
   DashboardMetric_objects = []
   for merchant_id, revenue in ledger_truth.items():
        for merchant in merchants:
            if merchant.merchant_id == merchant_id:
                currency = merchant.currency
                break
        dashboard_metric = DashboardMetric(
            merchant_id=merchant_id,
            revenue=revenue,
            currency=currency,
            period_start=period_start,
            period_end=period_end,
            pipeline_run_id="run_1"
        )

        DashboardMetric_objects.append(dashboard_metric)

   return DashboardMetric_objects
if __name__ == "__main__":

    merchants = generate_merchants(7)

    payments = generate_payments(merchants, 17)

    refunds = generate_refunds(payments, 10)

    ledger_entries = generate_ledger_entries(payments, refunds)

    period_start = datetime(2026, 6, 1)
    period_end = datetime(2026, 6, 30, 23, 59, 59)

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

    print("\n=== Dashboard Metrics ===")

    for metric in dashboard_metrics:
        print(
            f"{metric.merchant_id} | "
            f"Dashboard Revenue: {metric.currency} {metric.revenue} | "
            f"Period: {metric.period_start.date()} to {metric.period_end.date()} | "
            f"Pipeline Run: {metric.pipeline_run_id}"
        )