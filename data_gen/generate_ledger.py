import random

from data_gen.models import LedgerEntry
from data_gen.generate_merchants import generate_merchants
from data_gen.generate_payments import generate_payments


entry_types = ["payment", "refund", "settlement"]


def generate_ledger_entries(payments, count):

    ledger_entries = []

    for i in range(count):

        entry_id = f"entry_{i+1}"

        # The ledger entry is connected to an existing payment
        selected_payment = random.choice(payments)

        payment_id = selected_payment.payment_id
        merchant_id = selected_payment.merchant_id
        currency = selected_payment.currency

        entry_type = random.choice(entry_types)

        # For the initial M1 dataset,
        # use the payment amount as the base ledger amount.
        amount = selected_payment.amount

        timestamp = selected_payment.timestamp

        ledger_entry = LedgerEntry(
            entry_id=entry_id,
            payment_id=payment_id,
            merchant_id=merchant_id,
            entry_type=entry_type,
            amount=amount,
            currency=currency,
            timestamp=timestamp
        )

        ledger_entries.append(ledger_entry)

    return ledger_entries


if __name__ == "__main__":

    merchants = generate_merchants(7)

    payments = generate_payments(merchants, 17)

    ledger_entries = generate_ledger_entries(payments, 20)

    for entry in ledger_entries:
        print(
            f"{entry.entry_id} | "
            f"payment: {entry.payment_id} | "
            f"merchant: {entry.merchant_id} | "
            f"{entry.entry_type} | "
            f"{entry.currency} {entry.amount} | "
            f"{entry.timestamp}"
        )