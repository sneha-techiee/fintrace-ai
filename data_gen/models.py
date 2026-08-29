from dataclasses import dataclass
from datetime import datetime # as the merchant has onboarded_at .. some time 
# We need to represent that as a date/time.
from decimal import Decimal #Decimal- Decimal is a class for decimal arithmetic., decimal - module 
# dataclass is a decorator that helps Python automatically create common code for a class that mainly stores data.
@dataclass # a decorator
class Merchant: # create a class called merchant and make it a dataclass
    merchant_id : str
    name : str
    category : str
    currency : str
    onboarded_at : datetime
# The : str and : datetime parts are type hints.
# the above is the information that every merchant must contain 

# The relationship in our objects is as follows:-
# merchant -> payment -> Refund -> LedgerEntry -> PipelineRun
@dataclass
class Payment:
    payment_id : str
    merchant_id : str
    amount : Decimal # decimal is better suited for money/financial calculations, u could use float but It's a different numerical representation designed for cases where decimal precision and rounding rules matter
    currency : str
    status : str
    timestamp : datetime
 
# now, Refund 
@dataclass
class Refund:
    refund_id : str
    payment_id : str
    merchant_id : str
    amount : Decimal # less than or equal to payment ofc 
    status : str
    currency : str
    timestamp : datetime

@dataclass
class Settlement: #A Settlement represents money being settled for a merchant.
    settlement_id: str
    merchant_id: str
    payment_id: str
    amount: Decimal
    currency: str
    status: str
    timestamp: datetime

@dataclass
class LedgerEntry: #A LedgerEntry represents what actually gets recorded in our financial ledger
    entry_id: str
    payment_id: str
    merchant_id: str
    entry_type: str
    amount: Decimal
    currency: str
    timestamp: datetime
    direction : str