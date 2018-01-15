# This Python file uses the following encoding: utf-8
import numpy as np
import os, sys
import matplotlib.pyplot as plt
import transaction_utils as utils
from dataset import transaction_data
from params import *

'''
Valid commands (short-hand versions of the commands are also available, as seen below):
        
income, income all, income total, income categorized, income category <followed by category name>    
expenditure, expenditure all, expenditure total, expenditure categorized, expenditure category <followed by category name>  
all, undocumented, search <followed by words to search for in transaction description>, sort <followed by the name of a category>

Categories
expenditures  - grocery stores, item stores, restaurants, bars, medical, gym, subscriptions, rent, transportation, services, study expenses, holiday, vipps
Income        - student_loan, family, work_income


Full list of commands and what they do:
all            - gives you all transactions from the time period specified
inc            - gives you all transactions where money was received
exp            - gives you all transactions where money was spent
uncategorized  - gives you all transactions that hasn't been categorized

inc all                    - gives you all transactions where money was received 
inc total                  - gives you the total income in given time period
inc monthly                - gives you all income sorted by month
inc categorized            - gives you all income sorted by category
inc category <category>    - gives you all transactions in the category

exp all                    - gives you all expenditures in given time frame 
exp total                  - gives you the total expenditure in given time period
exp monthly                - gives you all expenditure sorted by month
exp categorized            - gives you all expenditures sorted by category
exp category <category>    - gives you all transactions in the category

search <transaction description>    - gives all transactions containing the description you search for
sort <category>                     - gives total sum of a category sorted by month

'''

# initialize the printout string given to the user when writing the command 'info'
def create_information_string():
    string = 'List of commands and what they do: \n'
    commands = ['all \t\t','income \t\t','expenditure \t','uncategorized \t','income all\t','income total\t', 'income monthly\t', 
                'income categorized','income category\t','expenditure all\t','expenditure total','expenditure monthly',
                 'expenditure categorized',  'expenditure category', 'sort <category>\t','plot\t\t','save\t\t', 'search <transaction description>' ]
    
    descriptions =  ['gives you all transactions from the time period specified','gives you all transactions where money was received',
                     'gives you all transactions where money was spent', 'gives you all transactions that has not been categorized', 
                     'gives you all transactions where money was received (as with the command "income" alone) ','gives you the total income in given time period',
                'gives you all income sorted by month','gives you all income sorted by category','gives you all transactions in the category',
                'gives you all expenditures in given time frame (as with the command "expenditure" alone) ', 'gives you the total expenditure in given time period',  
                'gives you all expenditure sorted by month','gives you all expenditures sorted by category', 
                 'gives total sum of a category sorted by month','gives you all transactions in the category','Gives you a bar-chart and pie-chart of the previous data',
                 'Saves previous data to a file','gives all transactions containing the description you search for' ]
    
    # add commands
    for i in range(0,len(commands)-1):
        string += commands[i]+'\t\t - '+descriptions[i]+'\n'
    string += commands[len(commands)-1]+' - '+descriptions[len(descriptions)-1]+'\n'  
    
    # add categories
    string += '\nHere is a list of all categories:\n'+'Incomes: \t'+', '.join(known_inc_array_identifiers)+'\nExpenditures: \t'+', '.join(known_exp_array_identifiers)          
    return string
    

if __name__ == "__main__":    
    # Initialize dataset
    filename = "sb2017.txt"        
    dataset = transaction_data(filename) 
    info = create_information_string()
    input, input_string = ' ','_'
    
    #receive input and process as long as it's not empty or 'exit'
    while len(input) != 0 and input != 'exit':
        print '\n----------------\nEnter a command to see the information you wish to see. For a list of valid commands, type "info".'
        input = raw_input("Command: ")
        
        
        # show info file
        if input=='info':
            print info
        # save previous entry
        elif input == 'save':
            file = open('transactions_output_'+input_string+'.txt','w') 
            if len(dataset.output_print) > 4:
                file.write(dataset.output_print.strip())
                file.close()
            else:
                print "There was no information to be saved."
                break
        elif input == 'plot':
            try:
                utils.simple_barchart(dataset.output_total, dataset.output_label)
                utils.simple_piechart(dataset.output_total, dataset.output_label)
            except:
                print 'Could not plot data.'    
        # execute command
        else:
            #print 'Enter the month from which you would like to see data (leave blank for january)'
            from_month = raw_input("From (month): ").strip()
            #print 'Enter the month after which you do not want to see data (leave blank for december)'
            to_month = raw_input("To (month): ").strip()

            #make the entire year standard search if fields are left blank
            if len(input) < 1:
                break
            if len(from_month) < 1:
                from_month = 'january'
            if len(to_month) < 1:
                to_month = 'december'
                
            # Perform query
            print '\n'               
            dataset(input,from_month,to_month)
            print dataset.output_print
            input_string = input.replace(' ', '_')
            
            