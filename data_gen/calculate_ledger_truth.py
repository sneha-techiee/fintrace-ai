# M2 = independently calculate what the financial ledger says
# the revenue should be, so later we can compare it against
# what the dashboard claims.

# Job of this file:
# Take our already-generated LedgerEntry objects and calculate
# the actual total for each merchant.
#
# credit → add money
# debit  → subtract money

# This tells us According to the actual financial ledger, this is the revenue

from decimal import Decimal
from data_gen.models import LedgerEntry
from data_gen.models import Refund
from data_gen.generate_payments import generate_payments
from data_gen.generate_merchants import generate_merchants 
from data_gen.generate_refunds import generate_refunds 
from data_gen.generate_ledger import generate_ledger_entries
from datetime import datetime


def calculate_ledger_truth(ledger_entries, period_start, period_end):
    merchant_totals = {}

    # Inspect every ledger entry
    for entry in ledger_entries:
        if not (period_start <= entry.timestamp <= period_end):
            continue
        merchant_id = entry.merchant_id

        # If this is the first entry we see for this merchant,
        # start their total at zero.
        if merchant_id not in merchant_totals:
            merchant_totals[merchant_id] = Decimal("0.00")

        # Apply the financial movement
        if entry.direction == "credit":
            merchant_totals[merchant_id] += entry.amount

        else:
            merchant_totals[merchant_id] -= entry.amount

    return merchant_totals
if __name__ == "__main__":

    merchants = generate_merchants(7)

    payments = generate_payments(merchants, 17)

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

    ledger_entries = generate_ledger_entries(
    payments,
    refunds
)
    period_start = datetime(2026, 6, 1)
    period_end = datetime(2026, 6, 30, 23, 59, 59)
    merchant_totals = calculate_ledger_truth(ledger_entries, period_start, period_end)

    for merchant_id, total in merchant_totals.items():
       print(f"{merchant_id} | Ledger Truth: {total}")

    
