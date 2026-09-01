# The job of this file is:
# Collect financial records that may be relevant to an incident.
#
# This file must NOT decide the root cause.
#
# Incident
#    ↓
# Evidence scope
#    ├── Payments
#    ├── Ledger entries
#    └── Pipeline runs (later)
#
# The AI investigator will examine this evidence
# and determine what actually happened.


from datetime import timedelta

LOOKBACK_WINDOW = timedelta(days=2)


def gather_payments_in_scope(
    incident,
    payments,
    period_start,
    period_end
):

    return [
        payment
        for payment in payments
        if (
            payment.merchant_id == incident.merchant_id
            and payment.currency == incident.currency
            and period_start - LOOKBACK_WINDOW
            <= payment.timestamp
            <= period_end + LOOKBACK_WINDOW
        )
    ]


def gather_ledger_entries_in_scope(
    incident,
    ledger_entries,
    period_start,
    period_end
):

    return [
        entry
        for entry in ledger_entries
        if (
            entry.merchant_id == incident.merchant_id
            and entry.currency == incident.currency
            and period_start - LOOKBACK_WINDOW
            <= entry.timestamp
            <= period_end + LOOKBACK_WINDOW
        )
    ]


def gather_evidence(
    incident,
    payments,
    ledger_entries,
    period_start,
    period_end
):

    return {
        "incident": incident,
        "payments": gather_payments_in_scope(
            incident,
            payments,
            period_start,
            period_end
        ),
        "ledger_entries": gather_ledger_entries_in_scope(
            incident,
            ledger_entries,
            period_start,
            period_end
        )
    }


if __name__ == "__main__":

    from data_gen.generate_merchants import generate_merchants
    from data_gen.generate_payments import generate_payments
    from data_gen.generate_refunds import generate_refunds
    from data_gen.generate_ledger import generate_ledger_entries
    from data_gen.calculate_ledger_truth import calculate_ledger_truth
    from data_gen.generate_dashboard_metrics import generate_dashboard_metrics
    from data_gen.simulate_duplicate_payment import simulate_duplicate_payment
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

    # target_merchant_id = None

    # for entry in ledger_entries:

    #     if (
    #         entry.entry_type == "refund"
    #         and period_start <= entry.timestamp <= period_end
    #     ):
    #         target_merchant_id = entry.merchant_id
    #         break

    # if target_merchant_id is None:
    #     print("No suitable refund found. Try running again.")
    #     exit()

    target_merchant_id = None

    for payment in payments:

        if period_start <= payment.timestamp <= period_end:
            target_merchant_id = payment.merchant_id
            break

    if target_merchant_id is None:
        print("No suitable payment found. Try running again.")
        exit()

    result = simulate_duplicate_payment(
        dashboard_metrics,
        payments,
        ledger_entries,
        target_merchant_id,
        period_start,
        period_end
    )

    if result is None:
        print(
            f"No duplicable payment found for merchant "
            f"{target_merchant_id}. Try running again."
        )
        exit()

    faulty_dashboard_metrics, incident_type = result

    incidents = detect_incidents(
        ledger_truth,
        faulty_dashboard_metrics,
        incident_type
    )

    print("\n=== Evidence Scope Test ===")

    for incident in incidents:

        evidence = gather_evidence(
            incident,
            payments,
            ledger_entries,
            period_start,
            period_end
        )

        print(
            f"\nIncident: {incident.incident_id}"
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
            f"\nPayments in scope: "
            f"{len(evidence['payments'])}"
        )

        for payment in evidence["payments"]:
            print(
                f"  {payment.payment_id} | "
                f"{payment.currency} "
                f"{payment.amount} | "
                f"{payment.status}"
            )

        print(
            f"\nLedger entries in scope: "
            f"{len(evidence['ledger_entries'])}"
        )

        for entry in evidence["ledger_entries"]:
            print(
                f"  {entry.entry_id} | "
                f"{entry.entry_type} | "
                f"{entry.currency} "
                f"{entry.amount} | "
                f"Payment: {entry.payment_id}"
            )