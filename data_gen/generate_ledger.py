# ledger is like a record of every financial movement 

# remember our ledger should always use the actual objects from paymebts and refunds 
#payment ledger entry → comes from an actual Payment
# refund ledger entry → comes from an actual Refund
# settlement → do not generate from payments randomly for the revenue ledger
# direction:
# payment → credit
# refund → debit
#  this is how our ledger should be 
# import random

from data_gen.models import LedgerEntry
from data_gen.generate_merchants import generate_merchants
from data_gen.generate_payments import generate_payments
from data_gen.generate_refunds import generate_refunds 


# entry_types = ["payment", "refund"]
#payment = credit
#refund = debit
#settlement = debit, because money is paid out to te merchant 
# and this logic is actually doing the same 
# we are Creating a ledger entry for each actual Payment and each actual Refund.
# def generate_ledger_entries(payments, refunds, count):

#     ledger_entries = []

#     for i in range(count):

#         entry_id = f"entry_{i+1}"

#         entry_type = random.choice(entry_types)

#         if entry_type == "payment":

#             selected_payment = random.choice(payments)

#             payment_id = selected_payment.payment_id
#             merchant_id = selected_payment.merchant_id
#             currency = selected_payment.currency
#             amount = selected_payment.amount
#             timestamp = selected_payment.timestamp
#             direction = "credit"

#         else:

#             selected_refund = random.choice(refunds)

#             payment_id = selected_refund.payment_id
#             merchant_id = selected_refund.merchant_id
#             currency = selected_refund.currency
#             amount = selected_refund.amount
#             timestamp = selected_refund.timestamp
#             direction = "debit"

#         ledger_entry = LedgerEntry(
#             entry_id=entry_id,
#             payment_id=payment_id,
#             merchant_id=merchant_id,
#             entry_type=entry_type,
#             amount=amount,
#             currency=currency,
#             timestamp=timestamp,
#             direction=direction
#         )

#         ledger_entries.append(ledger_entry)

#     return ledger_entries

# each payment each refund
# We're avoiding duplicate selection because we're iterating through every object exactly once.
def generate_ledger_entries(payments, refunds):

    ledger_entries = []
    entry_number = 1

    # Every actual Payment gets exactly one ledger entry
    for payment in payments:

        ledger_entry = LedgerEntry(
            entry_id=f"entry_{entry_number}",
            payment_id=payment.payment_id,
            merchant_id=payment.merchant_id,
            entry_type="payment",
            amount=payment.amount,
            currency=payment.currency,
            timestamp=payment.timestamp,
            direction="credit"
        )

        ledger_entries.append(ledger_entry)
        entry_number += 1

    # Every actual Refund gets exactly one ledger entry
    for refund in refunds:

        ledger_entry = LedgerEntry(
            entry_id=f"entry_{entry_number}",
            payment_id=refund.payment_id,
            merchant_id=refund.merchant_id,
            entry_type="refund",
            amount=refund.amount,
            currency=refund.currency,
            timestamp=refund.timestamp,
            direction="debit"
        )

        ledger_entries.append(ledger_entry)
        entry_number += 1

    return ledger_entries

if __name__ == "__main__":

    merchants = generate_merchants(7)

    payments = generate_payments(merchants, 17)

    refunds = generate_refunds(payments, 10)

    ledger_entries = generate_ledger_entries(payments, refunds)

    for entry in ledger_entries:
        print(
            f"{entry.entry_id} | "
            f"payment: {entry.payment_id} | "
            f"merchant: {entry.merchant_id} | "
            f"{entry.entry_type} | "
            f"{entry.currency} {entry.amount} | "
            f"{entry.timestamp} | "
            f"{entry.direction}"
        )