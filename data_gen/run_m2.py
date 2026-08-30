 # run_m2.py
#    │
#    ├── 1. create merchants
#    │
#    ├── 2. create payments USING those merchants
#    │
#    ├── 3. create refunds USING those payments
#    │
#    ├── 4. create ledger entries USING those payments + refunds
#    │
#    └── 5. calculate ledger truth USING those ledger entries
from data_gen.generate_merchants import generate_merchants
from data_gen.generate_payments import generate_payments
from data_gen.generate_refunds import generate_refunds
from data_gen.calculate_ledger_truth import calculate_ledger_truth
from data_gen.generate_ledger import generate_ledger_entries
from datetime import datetime
from faker import Faker 
if __name__ == "__main__":
     # 1. Create merchants
    merchants = generate_merchants(7)

    # 2. Create payments using those merchants
    payments = generate_payments(merchants, 17)

    # 3. Create refunds using those payments
    refunds = generate_refunds(payments, 10)

    # 4. Create ledger entries using the SAME payments and refunds
    ledger_entries = generate_ledger_entries(payments, refunds)

    # 5. Define our fixed reporting period
    period_start = datetime(2026, 6, 1)
    period_end = datetime(2026, 6, 30, 23, 59, 59)
    # 6. Calculate independent ledger truth for that period
    merchant_totals = calculate_ledger_truth(
        ledger_entries,
        period_start,
        period_end
    )

    # 7. Display the result
    print("\n=== M2 Ledger Truth ===")

    for merchant_id, total in merchant_totals.items():
        print(f"{merchant_id} | Ledger Truth: {total}")
