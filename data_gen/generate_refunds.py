import random
from faker import Faker
from decimal import Decimal
from datetime import datetime
from data_gen.models import Refund
from data_gen.generate_payments import generate_payments
from data_gen.generate_merchants import generate_merchants 
status_categories = ["ongoing", "completed", "failed"]
def generate_refunds(payments, count, period_end):
    fake = Faker()
    refunds =[]
    completed_payments = [
             payment for payment in payments
        if payment.status == "completed"
    ]  
    if not completed_payments:
        return refunds
    remaining_amounts = {
    payment.payment_id: payment.amount
    for payment in completed_payments
}
#Every refund corresponds to an actual completed payment, and a payment can have multiple refunds
# then your current approach is valid. In fact, this can be realistic because a payment could theoretically have multiple refund events, provided we also enforce that the total refunded amount doesn't exceed the payment amount.
# so, approach is a payment can have multiple refunds but some of refunds cant exceed the actual payment
# Total refunds ≤ Payment amount
    for i in range(count):
        refund_id = f"refund_{i+1}"
        eligible_payments = [
    payment for payment in completed_payments
    if remaining_amounts[payment.payment_id] > Decimal("0.00")

]
        if not eligible_payments:
          break
        selected_payments = random.choice(eligible_payments)
        # proceed only is payment is already done
        payment_id = selected_payments.payment_id
        merchant_id = selected_payments.merchant_id
            # i want to Give me 10 refunds, and each refund must be based on one of those completed payments
        # amount - it should be less than selected_payments amount 
        # amount = Decimal(str(random.uniform(0.01, float(selected_payments.amount)))).quantize(Decimal("0.01"))
        remaining = remaining_amounts[selected_payments.payment_id]

        amount = Decimal(
        str(random.uniform(0.01, float(remaining)))
).quantize(Decimal("0.01"))

        remaining_amounts[selected_payments.payment_id] = remaining - amount
        ## random.uniform() performs float-based arithmetic internally, so its inputs must be floats; Decimal + Decimal is valid in normal arithmetic, but cannot be used directly with uniform().
        currency = selected_payments.currency
        status = random.choice(status_categories)
        timestamp = fake.date_time_between(
           start_date=selected_payments.timestamp,
           end_date=period_end
)
# timestamp of refund is normally after the payment and current time for now
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

    period_end = datetime(2026, 6, 30, 23, 59, 59)

    refunds = generate_refunds(
        payments,
        10,
        period_end
    )

    for r in refunds:
        print(
            f"{r.refund_id} | "
            f"payment: {r.payment_id} | "
            f"merchant: {r.merchant_id} | "
            f"{r.currency} {r.amount} | "
            f"{r.status} | "
            f"{r.timestamp}"
        )



