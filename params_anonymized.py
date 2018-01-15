import numpy as np

#other
from_self = ['write down a phrase here that is unique to transfers from your own account']   #transfers from my own account
to_self = ['write down a phrase here that is unique to transfers to your own account']     #transfers to my own account
monthname = ['january', 'february', 'march', 'april', 'may', 'june', 'july',
              'august', 'september', 'october', 'november', 'december'] 

#expected expenditure categories (most entries are removed for privacy)
grocery_stores      = ['kiwi',  'bunnpris', 'coop extra', 'rema', 'rimi',
                        'coop mega', 'esso', 'meny', 'duty-free', 'joker']
item_stores         = ['elkjop','lefdal', 'g sport', 'hm.com',  
                       'clas ohlson', 'netonnet', 'komplett' ]
restaurants         = ['name of restaurant']
bars                = [ 'name of bar', 'vinmonopolet']
medical             = [ 'apotek','helfo','vitusapotek', 'legevakt' ]
gym                 = ['name of gym']
subscriptions       = ['audible', 'spotify', 'netflix' ]
rent                = ['description of rent-transactions']
vipps               = ['vipps by dnb'] #vipps won't tell you where you bought something, so their transactions are harder to sort
services            = ['hair dresser', 'cinema','name of regular service provider']
study_expenses      = ['description of uiversity transaction','name of place i buy books for academic purposes']
holiday             = ['transaction description from place i visited']
transportation      = ['name of buss service', 'name of train service', 'nok 33.00 vipps', 'nok 93.00 vipps'] # vipps entries are prices for buss/train
known_expenditures  = grocery_stores + item_stores + restaurants + bars + medical + gym + subscriptions + rent + transportation + services + study_expenses + holiday + vipps
known_exp_array     = np.array([grocery_stores, item_stores, restaurants, bars, medical, gym, subscriptions, rent, transportation, services, study_expenses, holiday, vipps])
known_exp_array_identifiers = ['grocery stores' , 'item stores' , 'restaurants' , 'bars' , 'medical' , 'gym' , 'subscriptions' ,
                                'rent' , 'transportation' , 'services' , 'study expenses' , 'holiday'  ,'vipps' ]

#expected income categories
student_loan    = ['student loan description']
other           = ['other regular source of money']
work_income     = ['description that is recognized as work income']
known_income    = student_loan + other + work_income
known_inc_array = np.array([student_loan , other , work_income])
known_inc_array_identifiers = ['student loan', 'family', 'work income']

known_source    = known_expenditures + known_income + to_self + from_self #income + expenditure
