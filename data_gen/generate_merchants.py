from math import floor # because of currency, math is a in built module and floor is a function like sqrt, ceil etc
from faker.providers import DynamicProvider
# generate_merchants.py tells python/ gives logic to python how to create many merchants. basically created merchant objects
# some, we ll control to avoid boring data, bcz we deliberately created properties like that .. and rest like name, onboarded_at will be created by faker .. 
# now from the faker package, we need a Faker class to get imported
from faker import Faker # check from this package's documentation , must to check from documentation to know the namings and everything
# module developers generally use packages lower case and class.. pascalcase eg: DataFrame, MyClass
fake = Faker() # i ve basically instantiated the class, created its object
from data_gen.models import Merchant
categories = ['ecommerce', 'subscriptions', 'marketplace']
category_provider = DynamicProvider(
             provider_name = "category",
             elements = categories
          )
fake.add_provider(category_provider)
def generate_merchants(count = 4): 
    inr_count = floor(0.75*count)# defined a function where i ve taken a default argument count as 4 .. as if nobody decides to take some other number, it by default is gonna be 4 as decided in M0
    usd_count = count - inr_count
    merchants =[] # this we ll use in payments as well
# count is a parameter, it represents how many merchants a caller wants.
# count = 4, default argument
    for i in range (count):# python uses zero-based indexing, range starts from zero by default 
# to discover what faker provides, what they actually mean and how to use them
        
    #    print(fake.name())
    #    print(fake.company()) // to generate a company/merchant name 
    #    print(fake.date_time_between()) #We decided in M0 that our synthetic merchants should have been onboarded within a reasonable recent period.
# by default its startin date is 30 years ago and end date is now now read the above comment, makes more sense 
# but we dont need merchant_id to be fake, i am gonna generate it myself
# category and currency is also something that i am controlling    
       merchant_id = f"merch_{i+1}" # placed i+1 inside {} to tell python to evaluate the expression and insert its result 
       name = fake.company()
       onboarded_at = fake.date_time_between()
# category and currency are not faker generated thehy are controlled by us 
# currency = 0.75 * count will be INR and rest USD but converting decimal into whole number : python's math module provides floor() means take a decimal and go down to the nearest whole number
       if i<inr_count:
           currency = "INR"
       else:
           currency = "USD"
# this above determines which exactly is a INR and Which USD 
# Category .. last property of mechant according to what we decided 
# Category :- our M0 design says merchants can belong to categories such as : ecommerce, suscriptions, marketplace \
# but remember Faker generates realistic values where randomness makes sense.
# We control values where our business rules matter
# right now we ll use 3 categories acc to our business rules but they can be any number of ..
    
# beauty of faker - we define the categories and faker can randomly choose from them 
# as here we want CONTROLLED RANDOMNESS

# from faker's documentation -   Dynamic providers can read elements from an external source.

# just for reference 
# from faker import Faker
# from faker.providers import DynamicProvider

# medical_professions_provider = DynamicProvider(
#      provider_name="medical_profession",
#      elements=["dr.", "doctor", "nurse", "surgeon", "clerk"],
# )

# fake = Faker()

# # then add new provider to faker instance
# fake.add_provider(medical_professions_provider)

# # now you can use:
# fake.medical_profession()
# # 'dr.'
       category = fake.category()
       merchant = Merchant(
            merchant_id=merchant_id,
            name=name,
            category=category,
            currency=currency,
            onboarded_at=onboarded_at
        )
       merchants.append(merchant)

    return merchants
         
# Add this at the bottom of generate_merchants.py
if __name__ == "__main__": # __main__ is a special string that is the python's way of sayin that this is the main file being run
    merchants = generate_merchants(4)
    for m in merchants:
        print(m)  