# Here is how to create  lots of payments 
from data_gen.models import Payment
from faker import Faker
from decimal import Decimal 
from datetime import datetime
import random # i do ve exisitng objects i just needed them randomly so i am gonna use random.choice from random, also i needed with replacement 
# we decided that payments will need exisitng merchants
from data_gen.generate_merchants import generate_merchants
def generate_payments(merchants, count): # no need to import merchants because python already knows it as it is a parameter
    payments = [] # here we are going to collect and store our created payment objects 
    fake = Faker()
    status_categories = [ 'ongoing', 'completed', 'failed']
    period_start = datetime(2026, 6, 1)
    period_end = datetime(2026, 6, 30, 23, 59, 59)
    for i in range(count):
        payment_id = f"pay_{i+1}"
        selected_merchants = random.choice(merchants)
        merchant_id = selected_merchants.merchant_id
        currency = selected_merchants.currency
        timestamp = fake.date_time_between(
            start_date= period_start,
            end_date= period_end
        )
        status = random.choice(status_categories)
        # to write te  amount lets understand decimal first - we need two conceptual operations
# first of all we want to generate a random monetory value - random module we ll use 
#  now Randint() - random module has a function called randint() that generates a random integer between two specified values.
# random.randint(start, end) start- minimum value and end is the maximum value
# Randint()- whole number, uniform()- random floating-point number 
# i think money can be floating point - we ll prbly use uniform()

# quantize() - Decimal("0.01")
        amount = Decimal(str(random.uniform(10, 10000))).quantize(Decimal("0.01"))
# status - completed, pending or failed 
        payment = Payment(

            payment_id = payment_id,
            merchant_id = merchant_id,
            amount = amount, # decimal is better suited for money/financial calculations, u could use float but It's a different numerical representation designed for cases where decimal precision and rounding rules matter
            currency = currency,
            status =status,
            timestamp =timestamp
        )
        payments.append(payment)
    return payments

if __name__ == "__main__":
    merchants = generate_merchants(7)

    payment = generate_payments(merchants, 17)  
    for p in payment:
        #   print(p)
        # we ll write readable output
       print( f"{p.payment_id} |"
        f"Merchant: {p.merchant_id} |"
        f"{p.currency} {p.amount} | "
        f"{p.status} | "
        f"{p.timestamp}"
    )   
# now we need to link merchants to it, we have a list of merchants and we need to randomly select any from it, this will be done by faker 
''' selected_merchant = one Merchant object

NOT merely its ID.

Why the entire object?

Because then you can access:

selected_merchant.merchant_id
selected_merchant.currency
selected_merchant.onboarded_at '''
       








