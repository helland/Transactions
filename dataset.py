import os, sys
import numpy as np
import transaction_utils as utils
from itertools import imap

'''
transaction data object that stores and handles the data.
It takes in the user's command and changes its stored data accordingly.
'''
class transaction_data(object):
    # constructor
    def __init__(self, filepath):
        self.dates = []
        self.notes = []
        self.values = []
        
        # separate transaction data from file into dates, notes and values
        with open(filepath,'r') as f:
            j = 0 
            for line in f:
                words = line.split()  
                self.dates.append(words[0])             # first word = date
                self.values.append(float(words[1]))     # second word = value
                self.notes.append('')                   # the rest are part of the entry comment 
                for i in range(2, len(words)):
                    self.notes[j] += str(words[i])+' '
                    self.notes[j] = self.word_formatting(self.notes[j])
                j += 1

        self.output_dates   = []
        self.output_values  = []
        self.output_notes   = []
        self.output_print   = ' \n' # output printed in command line
        self.output_total   = 0                                 # one or more output values other than the standard data set
        self.output_label   = []                                # accompanying label to output_total
        
    def __call__(self, command, from_month, to_month):
        command_one, command_two = self.format_command(command)                                                     # split command into two and format them
        from_month, to_month = self.format_months(from_month, to_month)                                             # make sure the month interval is two integers
        self.reinitialize()                                 # reset output values
        
        #If statement from hell that processes all the different commands.
        if 'empty' in command_two:                          # if there's only one word in given command
            if 'all' in command_one:                        # output = all data
                self.cmd_all(from_month, to_month)                                                  
            elif 'inc' in command_one:                      # output = all income data
                self.cmd_inc(from_month, to_month)           
            elif 'exp' in command_one:                      # output = all expenditure data
                self.cmd_exp(from_month, to_month)    
            elif 'uncategorized' in command_one:            # output = all data that hasn't been categorized
                self.cmd_uncategorized(from_month, to_month)             
            else:
                print 'The command "'+command_one+' '+command_two+'" was not recognized.'                        
        else:
            #income data has been requested
            if 'inc' in command_one:  
                if 'all' in command_two:                                # output = all income data   
                    self.cmd_all_inc_or_exp(from_month, to_month, 1)
                elif 'total' in command_two:                            # output = total income in given interval
                    self.cmd_total(from_month, to_month, 0)
                elif 'monthly' in command_two:                          # output = income sorted by month
                    self.cmd_monthly(from_month, to_month, 1)
                elif 'categorized' in command_two:                      # output = all income by category
                    self.cmd_inc_categorized(from_month, to_month)
                elif 'category' in command_two:                         # output = all details about specified category
                    self.cmd_category(from_month, to_month, command_two)
                else:
                    print 'The command "'+command_one+' '+command_two+'" was not recognized. Valid Income commands: "Income" followed by "all", "total", "monthly", "categorized" or "category"' 
            # expenditure data has been requested
            elif 'exp' in command_one:                
                if 'all' in command_two:                                # output = all expenditure data
                    self.cmd_all_inc_or_exp(from_month, to_month, -1)
                elif 'total' in command_two:                            # output = total expenditure in given interval
                    self.cmd_total(from_month, to_month,1)
                elif 'monthly' in command_two:                          # output = expenditure sorted by month
                    self.cmd_monthly(from_month, to_month, -1)
                elif 'categorized' in command_two:                      # output = all expenditure by category
                    self.cmd_exp_categorized(from_month, to_month)
                elif 'category' in command_two:                         # output = all details about specified category
                    self.cmd_category(from_month, to_month, command_two)
                else:
                    print 'The command "'+command_one+' '+command_two+'" was not recognized. Valid Expenditure commands: "expenditure" followed by "all", "total", "monthly", "categorized" or "category"' 
            # after search, the second command is searched for in notes and all entries with given parameter is returned
            elif 'search' in command_one:
                self.cmd_search(command_two, from_month, to_month)
            # sort a category by month and return all entries
            elif 'sort' in command_one:
                self.cmd_sorted_category(from_month, to_month, command_two.strip())
            # category command again, in case income or expenditure was not writen in front
            elif 'category' in command_one:
                self.cmd_category(from_month, to_month, 'category '+command_two)
            else:
                print 'The command "'+command_one+' '+command_two+'" was not recognized.' 
        
    
    # replace norwegian characters and make everything lowercase
    def word_formatting(self,string):
        string = string.lower()
        string = string.replace('\xc5', 'aa' )
        string = string.replace('\xd8', 'o' )
        string = string.replace('\xe5', 'aa' )
        string = string.replace('\xc6', 'ae' )
        return string    
    
    # Make the data easier to read should you want to print it
    def format_output(self, dates, values, notes):
        self.output_dates = dates
        self.output_values = values
        self.output_notes = notes
        if len(values)>=1:
            self.output_print = '\nDate: \t        NOK: \t Description: \n\n'       # format raw data print
        for i in range(0,len(self.output_values)):
            if self.output_values[i] != 0:          # remove empty entries                     
                self.output_print += self.output_dates[i]+'\t'+str(int(self.output_values[i]))+'\t '+self.output_notes[i]+'\n'
        if type(self.output_total) == float or type(self.output_total) == int:  # If no value is assigned to output_total, make it the sum of values
            self.output_total = sum(self.output_values)
            self.output_print += '\nSum = '+str(self.output_total)
        else:                                                                   # if the output_total value has been filled, format it in print
            for i in range(0,len(self.output_total)):
                if len(str(self.output_label[i])) < 7:
                    self.output_print += '\n'+self.output_label[i]+':\t\t'+str(int(self.output_total[i]))    #add a tab if the label is particularly short
                else:
                    self.output_print += '\n'+self.output_label[i]+':\t'+str(int(self.output_total[i]))      # when the label is longer print with one tab fewer            
    
    #format the input command (spell check, strip spaces and separates words into a first and second part of the command)    
    def format_command(self,command):
        command = command.lower()
        
        #replace potential wrong commands (spell check)
        wc_inc = ['income','inntekt','intekt','inntekter','inncome','incom','incmoe','incomme', 'innc','iinc', 'in tekt', 'inc ome', 'in come']
        wc_exp = ['expenditure','exxp','utgift','utgifter','expenditur','expendituer', 'expendeture''epx','pex','utgitf', 'ut gift']     
        wc_unc = ['uncat','un categorized','ukategorisert','undocumented','ikke kategorisert','ikke-kategorisert','uncategory','uncategorised', 'un-categorized']     
        wc_src = ['serch','saerch','searhc','leit', 'let etter', 'leit etter', 'leitetter','letetter','finn']
        wc_srt = ['sorte','srot','soort','sorter','sortert']
        wc = wc_inc + wc_exp + wc_unc + wc_src + wc_srt     #wrong commands (that needs to be fixed in this spell-check)
        
        for i in range(len(wc)):
            if wc[i] in command and any(imap(command.__contains__, wc_inc)):    # replace misss-spellings and alternatives of income 
                command = command.replace(wc[i],'inc')
            elif wc[i] in command and any(imap(command.__contains__, wc_exp)):  # replace misss-spellings and alternatives of expenditure 
                command = command.replace(wc[i],'exp')
            elif wc[i] in command and any(imap(command.__contains__, wc_unc)):  # replace misss-spellings and alternatives of uncategorized 
                command = command.replace(wc[i],'uncategorized')
            elif wc[i] in command and any(imap(command.__contains__, wc_src)):  # replace misss-spellings and alternatives of search 
                command = command.replace(wc[i],'search')
            elif wc[i] in command and any(imap(command.__contains__, wc_srt)):  # replace misss-spellings and alternatives of sort 
                command = command.replace(wc[i],'sort')
        
        #no matter how many words, make all but the first word count as command number two
        commands = command.split()
        command_one = commands[0]
        command_two = ''
        if len(commands) < 2:
            command_two = 'empty'
        else:    
            for i in range(1,len(commands)):
                command_two += commands[i]+' ' 
        command_one.strip(), command_two.strip()
        
        #switch command order if a first-only-command is found in command two
        if any(imap(command_two.__contains__, ['inc','exp','uncategorized','search','sort'])):
            return command_two,command_one
        else:
            return command_one, command_two  

    # make sure the month interval is two integers in the right order (from < to)        
    def format_months(self,from_month, to_month):
        month_names = ['january', 'february', 'march', 'april', 'may', 'june', 'july',
              'august', 'september', 'october', 'november', 'december'] 
        m_names = ['januar', 'februar', 'mars', 'april', 'mai', 'juni', 'juli',
              'august', 'september', 'oktober', 'november', 'desember'] 
        # replace month by integer representing given month
        for i in range(len(month_names)):
            if str(from_month) in month_names[i] or str(from_month) in m_names[i]: 
                from_month = i+1
            if str(to_month) in month_names[i] or str(from_month) in month_names[i]: 
                to_month = i+1
        if int(from_month) > int(to_month):         # if 'from' is greater than 'to'
            return int(to_month), int(from_month)   # switch order
        else:
            return int(from_month), int(to_month)
    
    '''
    The following functions are related to input commands
    They are used in __call__
    '''
    # all action done when 'all' command is entered
    def cmd_all(self, from_month, to_month):
        dates, values, notes = utils.all_inc_and_exp_values(self.dates, self.values, self.notes, from_month, to_month)
        self.format_output(dates, values, notes)        

    # all action done when 'income' command is entered
    def cmd_inc(self, from_month, to_month):
        dates, values, notes = utils.all_inc_or_exp_values(self.dates, self.values, self.notes, from_month, to_month, 1)
        self.format_output(dates, values, notes)        

    # all action done when 'exp' command is entered
    def cmd_exp(self, from_month, to_month):
        dates, values, notes = utils.all_inc_or_exp_values(self.dates, self.values, self.notes, from_month, to_month, -1)
        self.format_output(dates, values, notes)      

    # all action done when 'uncategorized' command is entered
    def cmd_uncategorized(self, from_month, to_month):                       
        self.dates, self.values, self.notes = utils.timeframe(self.dates, self.values, self.notes, from_month, to_month)    #remove months outside given time frame
        dates, values, notes = utils.undocumented_entries(self.dates, self.values, self.notes)
        self.format_output(dates, values, notes)       

      
    # all action done when 'income categorized' command is entered
    def cmd_inc_categorized(self, from_month, to_month):
        self.output_total, self.output_label = utils.income_categorized(self.dates, self.values, self.notes, from_month, to_month) 
        self.output_print = 'Categorized income \n'    #print expenditure if fortegn is negative and we've just collected exp per month data           
        self.format_output([], [], [])  
 
    # all action done when 'expenditure categorized' command is entered
    def cmd_exp_categorized(self, from_month, to_month):
        self.output_total, self.output_label = utils.expenditure_categorized(self.dates, self.values, self.notes, from_month, to_month) 
        self.output_print = 'Categorized expenditure \n'    #print expenditure if fortegn is negative and we've just collected exp per month data           
        self.format_output([], [], [])  
    
    # all action done when 'search' command is entered
    def cmd_search(self,key_phrase, from_month, to_month): 
        dates, values, notes,self.output_total = utils.find_keyword(self.dates, self.values, self.notes, key_phrase.strip(), from_month, to_month)
        self.output_print = 'All transactions related to "'+key_phrase+'" \n'            
        self.format_output(dates, values, notes)  

 
        
    # all action done when 'income all' or 'expenditure all' command is entered
    def cmd_all_inc_or_exp(self, from_month, to_month, fortegn):                       
        dates, values, notes = utils.all_inc_or_exp_values(self.dates, self.values, self.notes, from_month, to_month, fortegn)   
        if fortegn < 0:         #change the printout depending on whether it's income or expenditure
            text = 'expenditure'
        else:
            text = 'income'
        self.output_print = 'All '+text+' from '+utils.monthname[from_month-1]+' to '+utils.monthname[to_month-1]+'\n'
        #self.output_total = 0                   # ugly correction to get sum printed (happens in format_output) 
        self.format_output(dates, values, notes)        

    # all action done when 'income monthly' or 'expenditure monthly' command is entered (depending on fortegn)
    def cmd_monthly(self, from_month, to_month, fortegn):
        self.output_total, self.output_label = utils.monthly(self.dates, self.values, self.notes, from_month, to_month, fortegn)
        if fortegn < 0:
            self.output_print = 'Monthly expenditure \n'    #print expenditure if fortegn is negative and we've just collected exp per month data
        else:
            self.output_print = 'Monthly income \n'         #print income if fortegn is positive and we've just collected exp per month data              
        self.format_output([], [], [])  
                   
    # all action done when 'income total' or 'expenditure total' command is entered
    def cmd_total(self, from_month, to_month,inc_or_exp):                       
        self.dates, self.values, self.notes = utils.timeframe(self.dates, self.values, self.notes, from_month, to_month)    #remove months outside given time frame
        self.output_total = [utils.total_io(self.values, self.notes)[inc_or_exp]]                                           #inc_or_exp decides if you extract income or expenditure data
        text = 'income'
        if inc_or_exp == 1:         #change the printout depending on whether it's income or expenditure
            text = 'expenditure'
        self.output_label = ['Total '+text+' from '+utils.monthname[from_month-1]+' to '+utils.monthname[to_month-1]]         # output print string
        self.format_output([], [], [])
        
    # all action done when 'income category' command is entered
    def cmd_sorted_category(self, from_month, to_month, category_identifier):   
        try:
            self.output_total, self.output_label = utils.sort_category_per_month(self.dates, self.values, self.notes, category_identifier, from_month, to_month)
            self.output_print = '"'+category_identifier+'" transactions per month \n'        
            self.format_output([], [], [])   
        except:
            #category name was invalid
            if len(category_identifier) > 0:    
                print '"'+category_identifier+'" is not a valid category to be sorted. \n\nHere is a list of all categories:\n'
                print 'Expenditures: '+', '.join(utils.known_exp_array_identifiers)
                print 'Incomes: '+', '.join(utils.known_inc_array_identifiers)           
            # no category was specified or something else went wrong
            else:                               
                print 'You need to specify category by writing its name after "sort"'   
        
    # all action done when 'income category' command is entered
    def cmd_category(self, from_month, to_month, command_two):   
        try:
            category_identifier = command_two.split(' ',1)[1].strip() #remove 'category' from the command and whitespaces at the start & end
            dates, values, notes, self.output_total = utils.category_details(self.dates, self.values, self.notes, category_identifier, from_month, to_month)
            if len(values) > 0:
                self.output_print = 'All entries in "'+category_identifier+'": \n'          
            else:
                self.output_print = 'No entries could be found in the category "'+category_identifier+'" \n'    
            self.format_output(dates, values, notes)   
        except:
            #category name was invalid
            if len(category_identifier) > 0:    
                print '"'+category_identifier+'" is not a valid category. \n\nHere is a list of all categories:\n'
                print 'Expenditures: '+', '.join(utils.known_exp_array_identifiers)
                print 'Incomes: '+', '.join(utils.known_inc_array_identifiers)           
            # no category was specified or something else went wrong
            else:                               
                print 'You need to specify category by writing its name after "category"'   
        
        
    # reset output values         
    def reinitialize(self):       
        self.output_dates   = []
        self.output_values  = []
        self.output_notes   = []
        self.output_print   = '\n \n'                           # output printed in command line
        self.output_total   = 0                                 # one or more output values other than the standard data set
        self.output_label   = []                                # accompanying label to output_total        
        
        
        
        
        
        