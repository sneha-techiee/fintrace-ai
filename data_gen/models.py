from dataclasses import dataclass
from datetime import datetime # as the merchant has onboarded_at .. some time 
# We need to represent that as a date/time.
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



