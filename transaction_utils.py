# This Python file uses the following encoding: utf-8

'''
Here you'll find utility functions used to find, sort and filter
the data. timeframe, returned_items, self_transfer and find_category 
are helping functions used in the others below.
'''

import os, sys
import numpy as np
from itertools import imap
from params import *
import matplotlib.pyplot as plt; plt.rcdefaults()
import matplotlib.pyplot as plt

import numpy as np


#reduce data set to specific months
def timeframe(dates, values, notes, from_month, to_month):
    new_dates, new_values, new_notes = [],[],[]
    #print 'timeframe set as ',monthname[from_month-1],' to ',monthname[to_month-1]
    for i in range(0,len(dates)):
        for j in range(from_month, to_month+1):
            if ('.0'+str(j)+'.' in dates[i] or '.'+str(j)+'.' in dates[i]):   #print '.0'+str(j)+'. or .'+str(j)+'.'                
                new_dates.append(dates[i])
                new_values.append(values[i]) 
                new_notes.append(notes[i])

    return new_dates, new_values, new_notes
 

#find how much money has been given by stores that don't hand out money, meaning the money comes from items being returned  
def returned_items(value, note): 
    if value > 0 and any(imap(note.__contains__, known_expenditures)) and not any(imap(note.__contains__, known_income)):
        return value
    else:
        return 0

# remove transfers to and from myself
def self_transfer(value, note):
    if (to_self[0] in note or from_self[0] in note): 
        return -value
    else:
        return 0

# returns category-array corresponding with input name  
def find_category(identifier):
    for i in range(0, len(known_inc_array_identifiers)):
        if identifier == known_inc_array_identifiers[i]:
            return known_inc_array[i]
    for i in range(0, len(known_exp_array_identifiers)):
        if identifier == known_exp_array_identifiers[i]:
            return known_exp_array[i]
    
#returns arrays of total income per month
def total_io(values, notes):
    income = 0
    spending = 0
    
    for i in range(0, len(values)-1):
            if  values[i] > 0:          # Income
                income += values[i]
                income += self_transfer(values[i], notes[i])    # remove transfers from myself
                spending += returned_items(values[i], notes[i]) # remove returned items from spending  
            elif values[i] < 0:         # Expenditure
                spending += values[i]
                spending += self_transfer(values[i], notes[i])  # remove transfers to myself              
    return income, spending

#returns all data, but corrected for (by removing self-transfers)
def all_inc_and_exp_values(dates, values, notes, from_month, to_month):
    dates, values, notes = timeframe(dates, values, notes, from_month, to_month) #shave off months outside desired time frame    
    new_dates, new_values, new_notes = [],[],[] # It would probably be more efficient to just remove self-transfers, but instead, we create new arrays and add everything but the unwanted
       
    for i in range(0, len(values)-1):   
        if  self_transfer(values[i], notes[i]) == 0:  #remove self-transfers  
            new_values.append(values[i])
            new_dates.append(dates[i])
            new_notes.append(notes[i])
           
    return new_dates, new_values, new_notes 

#returns all data in given interval. negative fortegn gives expenditures, positive gives income
def all_inc_or_exp_values(dates, values, notes, from_month, to_month, fortegn):
    dates, values, notes = timeframe(dates, values, notes, from_month, to_month) #shave off months outside desired time frame    
    new_dates, new_values, new_notes = [],[],[]
    
    for i in range(0, len(values)-1):   
        if fortegn*values[i] > 0 and self_transfer(values[i], notes[i]) == 0 and returned_items(values[i], notes[i]) == 0: #remove self-transfers and returned items 
            new_values.append(values[i])
            new_dates.append(dates[i])
            new_notes.append(notes[i])
        if fortegn*values[i] < 0 and returned_items(values[i], notes[i]) != 0:    #correction: returned items are added as expenditure (despite being positive value) to cancel out purchase 
            new_values.append(values[i])
            new_dates.append(dates[i])
            new_notes.append(notes[i])            
    return new_dates, new_values, new_notes 

# returns arrays of total spending or income per month given 'fortegn' - there's no english word for 'plus or minus' :(
def monthly(dates, values, notes, from_month, to_month, fortegn):
    monthly_values = np.zeros(12)
    months, values_subset = [],[]
        
    # sort all desired values by month
    for i in range(0, len(values)):
        for j in range(1,13):
            if ('.0'+str(j)+'.' in dates[i] or '.'+str(j)+'.' in dates[i]) and fortegn*values[i] > 0: #fortegn = +-1, so if we want expenditures, only negative values will go through
                monthly_values[j-1] += values[i]              
                monthly_values[j-1] += self_transfer(values[i], notes[i])    # remove transfers from myself
    # extract only the desired months
    for k in range(from_month,to_month+1):
        months.append(monthname[k-1])
        values_subset.append(monthly_values[k-1])
      
    return values_subset, months    

def expenditure_categorized(dates, values, notes, from_month, to_month):
    '''
        return total spending in above categories as an array.
        time interval is defined in months.
    '''        
    dates, values, notes = timeframe(dates, values, notes, from_month, to_month) #shave off months outside desired timeframe    
    categories = known_exp_array_identifiers                            # names of all categories
    categorized_spending = np.zeros(13)                                 # how much expenditure in each category
    
    for i in range(0, len(notes)):                                      # For every entry
        corr_counter = 0                                                # count number of categories an entry goes into
        corr_categories = []                                            # list categories the entry goes into
        for j in range(0,len(categorized_spending)):                    # For every category
            if any(imap(notes[i].__contains__, known_exp_array[j])):    # Check entry note for a match in given category
                categorized_spending[j] += values[i]                    # Add value to category if there's a match
                corr_counter += 1
                corr_categories.append(j)
        if corr_counter >= 2:                                           # if the entry went into more than one category                                                                                                 
            for k in corr_categories:                                       #print "Value number "+str(i)+" was placed into multiple categories", corr_categories
                categorized_spending[k] -= values[i]                    # remove the value from all categories it was put into  
            categorized_spending[corr_categories[0]] += values[i]       # add the value back into the first category, which has highest priority
            
    return categorized_spending, categories

def income_categorized(dates, values, notes, from_month, to_month):
    '''
        return total income in above categories as an array.
        time interval is defined in months.
    '''        
    dates, values, notes = timeframe(dates, values, notes, from_month, to_month) #shave off months outside desired timeframe    
    categories = known_inc_array_identifiers 
    categorized_income = np.zeros(3) 
    
    for i in range(0, len(notes)):                                      # For every entry
        for j in range(0,len(categorized_income)):                      # For every category
            if any(imap(notes[i].__contains__, known_inc_array[j])):    # Check entry note for a match in given category
                categorized_income[j] += values[i]                      # Add value to category if there's a match
        
    return categorized_income, categories

def category_details(dates, values, notes, category_identifier, from_month, to_month):
    '''
        return total income in one certain category as defined above.
        Also return every entry in said category.
        time interval is defined in months.
    '''        
    dates, values, notes = timeframe(dates, values, notes, from_month, to_month) #shave off months outside desired time frame    
    cat_dates, cat_values, cat_notes = [],[],[]
    category = find_category(category_identifier) 
    
    total = 0                                                           # total income in given category
    for i in range(0, len(notes)):                                      # For every entry
        if any(imap(notes[i].__contains__,category)):                   # Check entry note for a match in given category
            cat_dates.append(dates[i])
            cat_values.append(values[i])    
            cat_notes.append(notes[i])    
            total += values[i]                                          # Add value to category if there's a match
    return cat_dates, cat_values, cat_notes, total

# returns the total expenditure in a certain category for each month
def sort_category_per_month(dates, values, notes, category_identifier, from_month, to_month):
    dates, values, notes, _ = category_details(dates, values, notes, category_identifier, from_month, to_month)
    monthly_total = np.zeros(12)
    months, values_subset = [],[]
    for i in range(1,13):
        monthly_total[i-1] = sum(timeframe(dates, values, notes, i, i)[1])
        
    # extract only the desired months
    for k in range(from_month,to_month+1):
        months.append(monthname[k-1])
        values_subset.append(monthly_total[k-1])

    return values_subset, months
   
#look for entries with a certain phrase (for example: 'kiwi' to find all expenditures at a kiwi store)
def find_keyword(dates, values, notes, key_phrase, from_month, to_month):
    dates, values, notes = timeframe(dates, values, notes, from_month, to_month) #shave off months outside desired timeframe                                    
    kp_dates, kp_values, kp_notes = [],[],[]
    kp_total = 0
    
    for i in range(0, len(notes)):                                  # for every entry                                        
        if key_phrase in notes[i]:                                  # see of the key phrase is found in entry note
            kp_dates.append(dates[i])                               # store values if it finds a match
            kp_values.append(values[i])    
            kp_notes.append(notes[i])    
            kp_total += values[i]      
            
    return kp_dates,kp_values,kp_notes,kp_total
        
#return entries that has not been categorized above
def undocumented_entries(dates, values, notes):
    u_dates, u_values, u_notes = [],[],[]
    
    for i in range(0, len(notes)):
        if  any(imap(notes[i].__contains__, known_source)):
            continue
        else:
            u_dates.append(dates[i])
            u_values.append(values[i])    
            u_notes.append(notes[i]) 
    return u_dates,u_values,u_notes

'''
The functions below are used to print out various plots and charts.
They're used with the 'plot' command in main.
'''

def simple_plot(values,months):
    average = np.abs(sum(values)/len(months))
        
    plt.plot(months,np.abs(values), 'b-')
    plt.plot([1,12],[average,average], 'r--')
    plt.axis([min(months),max(months),0,max(np.abs(values))])
    plt.legend(['monthly','average'])
    
    print '\n'
    for i in range(min(months),max(months)): 
        print str(int(np.abs(values[i])))+',- was spent in '+monthname[i-1]
    print str(int(np.abs(average)))+',- was the average across this time period'
          
    plt.show()
        
# Pie chart, where the slices will be ordered and plotted counter-clockwise:
def simple_piechart(values,labels):    
    explode = np.zeros(len(values))  # add value if one or more category should pop out
    
    fig1, ax1 = plt.subplots()
    ax1.pie(np.abs(values), explode=explode, labels=labels, autopct='%1.1f%%',
            shadow=True, startangle=90)
    ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.    
    plt.show()

def simple_barchart(values,labels):     
    y_pos = np.arange(len(labels))

    plt.bar(y_pos, np.abs(values), align='center', alpha=0.5)
    plt.xticks(y_pos, labels)
    plt.ylabel('NOK')
    plt.show() 
    
    