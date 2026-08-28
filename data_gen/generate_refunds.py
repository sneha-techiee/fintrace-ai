import random
from faker import Faker
from decimal import Decimal
from data_gen.models import Refund
from data_gen.generate_payments import generate_payments
from data_gen.generate_merchants import generate_merchants 
status_categories = ["ongoing", "completed", "Failed"]
def generate_refunds(payments, count):
    refunds =[]
    for i in range(count):
        refund_id = f"refund_{i+1}"
        selected_payments = random.choice(payments)
        payment_id = selected_payments.payment_id
        merchant_id = selected_payments.merchant_id
        # amount - it should be less than selected_payments amount 
        amount = Decimal(str(random.uniform(0.01, float(selected_payments.amount)))).quantize(Decimal("0.01"))
        ## random.uniform() performs float-based arithmetic internally, so its inputs must be floats; Decimal + Decimal is valid in normal arithmetic, but cannot be used directly with uniform().
        currency = selected_payments.currency
        status = random.choice(status_categories)
        timestamp = selected_payments.timestamp

        refund = Refund(
        refund_id = refund_id,
            payment_id = payment_id,
            merchant_id = merchant_id,
            amount =amount, # less than or equal to payment ofc 
            status = status,
            currency = currency,
            timestamp = timestamp
)
        refunds.append(refund)
    return refunds
if __name__ == "__main__":
    merchants = generate_merchants(7)
    payments = generate_payments(merchants, 17)
    refunds = generate_refunds(payments, 10)

    for r in refunds:
        print(
            f"{r.refund_id} | "
            f"payment: {r.payment_id} | "
            f"merchant: {r.merchant_id} | "
            f"{r.currency} {r.amount} | "
            f"{r.status} | "
            f"{r.timestamp}"
        )



