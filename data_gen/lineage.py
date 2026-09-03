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