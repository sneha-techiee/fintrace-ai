import random
from decimal import Decimal

from data_gen.models import Settlement
from data_gen.generate_merchants import generate_merchants
from data_gen.generate_payments import generate_payments

# importin decimal isn't actually needed in generate_settlements.py, because we're not creating a new Decimal there, we're inheriting the existing Decimal from the Payment.
status_categories = ["ongoing", "completed", "failed"]


def generate_settlements(payments, count):

    settlements = []
    completed_payments = [
    payment for payment in payments
    if payment.status == "completed"
]
    if not completed_payments:
      return settlements


    

    for i in range(count):

        settlement_id = f"settle_{i+1}"
        selected_payment = random.choice(completed_payments)

        # A settlement must belong to an existing payment
       

        payment_id = selected_payment.payment_id
        merchant_id = selected_payment.merchant_id
        currency = selected_payment.currency

        # For our synthetic ecosystem,
        # settlement amount will be based on the payment amount.
        amount = selected_payment.amount

        status = random.choice(status_categories)

        timestamp = selected_payment.timestamp

        settlement = Settlement(
            settlement_id=settlement_id,
            merchant_id=merchant_id,
            payment_id=payment_id,
            amount=amount,
            currency=currency,
            status=status,
            timestamp=timestamp
        )

        settlements.append(settlement)

    return settlements


if __name__ == "__main__":

    merchants = generate_merchants(7)

    payments = generate_payments(merchants, 17)

    settlements = generate_settlements(payments, 10)

    for s in settlements:
        print(
            f"{s.settlement_id} | "
            f"payment: {s.payment_id} | "
            f"merchant: {s.merchant_id} | "
            f"{s.currency} {s.amount} | "
            f"{s.status} | "
            f"{s.timestamp}"
        )