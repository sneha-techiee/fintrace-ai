# The job of this file is:
# Trace an incident back to the financial record that caused it.
#
# Incident
#    ↓
# Refund
#    ↓
# Payment
#
# It helps us answer:
# "Which refund caused this revenue discrepancy?"

from data_gen.models import Incident, LedgerEntry


def find_refund_for_incident(incident, ledger_entries):

    for entry in ledger_entries:

        if (
            entry.merchant_id == incident.merchant_id
            and entry.entry_type == "refund"
            and entry.amount == incident.discrepancy
        ):
            return entry

    return None
def find_refunds_for_incident(incident, ledger_entries):
# Give me the refund records belonging to this merchant and currency.
    matching_refunds = []

    for entry in ledger_entries:

        if (
            entry.merchant_id == incident.merchant_id
            and entry.entry_type == "refund"
            and entry.currency == incident.currency
        ):
            matching_refunds.append(entry)

    return matching_refunds


def find_payment_for_refund(refund_entry, payments):

    for payment in payments:

        if payment.payment_id == refund_entry.payment_id:
            return payment

    return None


def investigate_incident(incident, ledger_entries, payments):

    refunds = find_refunds_for_incident(
        incident,
        ledger_entries
    )

    if not refunds:
        return None

    refund_entry = None

    for refund in refunds:
        if refund.amount == incident.discrepancy:
            refund_entry = refund
            break

    if refund_entry is None:
        return None

    payment = find_payment_for_refund(
        refund_entry,
        payments
    )

    return {
        "incident": incident,
        "refund": refund_entry,
        "payment": payment,
        "root_cause": "dashboard omitted a refund"
    }
    

if __name__ == "__main__":

    from data_gen.generate_merchants import generate_merchants
    from data_gen.generate_payments import generate_payments
    from data_gen.generate_refunds import generate_refunds
    from data_gen.generate_ledger import generate_ledger_entries
    from data_gen.calculate_ledger_truth import calculate_ledger_truth
    from data_gen.generate_dashboard_metrics import generate_dashboard_metrics
    from data_gen.simulate_incident import simulate_missing_refund
    from data_gen.detect_incidents import detect_incidents
    from datetime import datetime

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
        2026, 6, 1
    )

    period_end = datetime(
        2026, 6, 30, 23, 59, 59
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

    target_merchant_id = None

    for entry in ledger_entries:

        if (
            entry.entry_type == "refund"
            and period_start <= entry.timestamp <= period_end
        ):
            target_merchant_id = entry.merchant_id
            break

    faulty_dashboard_metrics = simulate_missing_refund(
        dashboard_metrics,
        ledger_entries,
        target_merchant_id
    )

    incidents = detect_incidents(
        ledger_truth,
        faulty_dashboard_metrics
    )

    print("\n=== Incident Investigation ===")

    for incident in incidents:

        result = investigate_incident(
            incident,
            ledger_entries,
            payments
        )

        if result is not None:

            refund = result["refund"]
            payment = result["payment"]

            print(
                f"Incident: {incident.incident_id}"
            )

            print(
                f"Merchant: {incident.merchant_id}"
            )

            print(
                f"Discrepancy: "
                f"{incident.currency} "
                f"{incident.discrepancy}"
            )

            print(
                f"Refund: "
                f"{refund.currency} "
                f"{refund.amount}"
            )

            print(
                f"Payment ID: "
                f"{refund.payment_id}"
            )

            if payment is not None:

                print(
                    f"Original Payment: "
                    f"{payment.currency} "
                    f"{payment.amount}"
                )
                print(
                f"Root Cause: {result['root_cause']}"
            )