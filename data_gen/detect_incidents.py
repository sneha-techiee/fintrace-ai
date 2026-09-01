# The job of this file is :- Compare the clean ledger truth with the faulty dashboard and create an Incident when they don't match.
from decimal import Decimal
from data_gen.models import Incident
def detect_incidents(ledger_truth, dashboard_metrics, incident_type):
    incidents = []

    for dashboard_metric in dashboard_metrics:

        merchant_id = dashboard_metric.merchant_id

        expected_revenue = ledger_truth.get(
            merchant_id,
            Decimal("0.00")
        )

        actual_revenue = dashboard_metric.revenue

        discrepancy = actual_revenue - expected_revenue
        if discrepancy != Decimal("0.00"):

            incident = Incident(
                incident_id=f"incident_{len(incidents) + 1}",
                merchant_id=merchant_id,
                incident_type=incident_type,              
                expected_revenue=expected_revenue,
                actual_revenue=actual_revenue,
                discrepancy=discrepancy,
                currency=dashboard_metric.currency,
                severity="high"
            )

            incidents.append(incident) 
    return incidents 
        