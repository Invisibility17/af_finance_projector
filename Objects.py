import datetime
import numpy as np
class Member():
    def __init__(self, personal, tax_sheet):
        self.rank           = personal.loc["Rank", "Value"]
        self.EAD            = personal.loc["EAD", "Value"]
        self.update_senority(datetime.datetime.now())

        self.zip_code       = personal.loc["BAH location", "Value"]

        self.married        = personal.loc["Married?", "Value"].lower() == "yes"
        self.dependents     = personal.loc["Dependents?", "Value"].lower() == "yes"

        self.other_income   = personal.loc["Other income", "Value"]
        self.cost_of_living = personal.loc["Cost of Living", "Value"]
        self.state_tax      = personal.loc["State Tax", "Value"]
        self.BRS            = personal.loc["BRS", "Value"].lower() == "yes"
        
        self.tax_sheet = tax_sheet

    def compute_taxes(self):
        rates = self.tax_sheet.loc[:,"Tax Rate"]
        if self.married:
            brackets    = self.tax_sheet.loc[:,"Married"]
            deduction   = self.tax_sheet.loc[0,"Standard Married Deduction"]
        else:
            brackets    = self.tax_sheet.loc[:,"Single"]
            deduction   = self.tax_sheet.loc[0,"Standard Single Deduction"]

        annual_taxed_pay = self.taxable_income
        fica_ceiling = self.tax_sheet.loc[0, "FICA Ceiling"]
        fica_rate = self.tax_sheet.loc[0,"FICA Rate"]
        if annual_taxed_pay > fica_ceiling:
            total_tax = (fica_ceiling * fica_rate)/100
        else:
            total_tax = (annual_taxed_pay * fica_rate)/100

        # Subtract standard deduction and calculate federal taxes
        annual_taxed_pay -= deduction
        total_tax += annual_taxed_pay * (rates[0] / 100)
        for i in range(1, len(rates), 1):
            if annual_taxed_pay > brackets[i-1]:
                total_tax += (annual_taxed_pay - brackets[i-1])*(rates[i]-rates[i-1])/100
            else:
                break
        self.fed_tax = total_tax
        return total_tax

    def update_senority(self, when):
        self.time_in_service = when-self.EAD
        self.senority = self.compute_TIS(when)
        
    def compute_TIS(self, when):
        # probably bounds the leap day error
        time_in_service = when-self.EAD
        if time_in_service < datetime.timedelta(days=2*365.2425):
            senority = 1
        elif time_in_service < datetime.timedelta(days=3*365.2425):
            senority = 2
        elif time_in_service < datetime.timedelta(days=4*365.2425):
            senority = 3
        elif time_in_service < datetime.timedelta(days=6*365.2425):
            senority = 4
        elif time_in_service < datetime.timedelta(days=8*365.2425):
            senority = 5
        elif time_in_service < datetime.timedelta(days=10*365.2425):
            senority = 6
        elif time_in_service < datetime.timedelta(days=12*365.2425):
            senority = 7
        elif time_in_service < datetime.timedelta(days=14*365.2425):
            senority = 8
        elif time_in_service < datetime.timedelta(days=16*365.2425):
            senority = 9
        elif time_in_service < datetime.timedelta(days=18*365.2425):
            senority = 10
        elif time_in_service < datetime.timedelta(days=20*365.2425):
            senority = 11
        elif time_in_service < datetime.timedelta(days=22*365.2425):
            senority = 12
        elif time_in_service < datetime.timedelta(days=24*365.2425):
            senority = 13
        elif time_in_service < datetime.timedelta(days=26*365.2425):
            senority = 14
        elif time_in_service < datetime.timedelta(days=28*365.2425):
            senority = 15
        elif time_in_service < datetime.timedelta(days=30*365.2425):
            senority = 16
        elif time_in_service < datetime.timedelta(days=32*365.2425):
            senority = 17
        elif time_in_service < datetime.timedelta(days=34*365.2425):
            senority = 18
        elif time_in_service < datetime.timedelta(days=36*365.2425):
            senority = 19
        elif time_in_service < datetime.timedelta(days=38*365.2425):
            senority = 20
        elif time_in_service < datetime.timedelta(days=40*365.2425):
            senority = 21
        else:
            senority = 22
        return senority

    def life_change(self, change_matrix):
        # Data Frame:
        #   Time Rank ZIP Base BAH BAS Married Dependents CoL State_Tax Other_Income
        self.total_income = 0
        self.taxable_income = 0
        month_index = 0
        this_year = 0
        for change in change_matrix.iterrows():
            this_year = change[1]["Time"].year
            months = change[1]["Time"].month - month_index # start AFTER the month of the change
            self.total_income += (self.base + self.bah + self.bas)*months
            self.taxable_income += self.base*months
            month_index = change[1]["Time"].month
            self.rank = change[1]["Rank"]
            self.zip_code = change[1]["ZIP"]
            self.base = change[1]["Base"]
            self.bah = change[1]["BAH"]
            self.bas = change[1]["BAS"]
            self.married = change[1]["Married"]
            self.dependents = change[1]["Dependents"]
            self.cost_of_living = change[1]["Cost of Living"]
            self.state_tax = change[1]["State Tax"]
            self.other_income = change[1]["Other Income"]
        self.total_income += (self.base + self.bah + self.bas)*(12 - month_index)
        self.taxable_income += (self.base)*(12 - month_index)
        self.total_income += self.other_income
        self.taxable_income += self.other_income
        self.compute_taxes()

        self.saved = self.total_income - self.fed_tax - self.state_tax - self.cost_of_living
        return self.saved
    
    """def update_income(self, new_extra_income):
        self.other_income = new_extra_income
        self.total_income = (self.base + self.bah + self.bas)*12 + self.other_income
        self.taxable_income = self.base*12 + self.other_income
        self.compute_taxes()
        self.saved = self.total_income - self.fed_tax - self.state_tax - self.cost_of_living

    def update_COL(self, new_col):
        self.cost_of_living = new_col
        self.saved = self.total_income - self.fed_tax - self.state_tax - self.cost_of_living"""
        
    def set_pay_allowances(self, base, bas, bah):
        self.base = base 
        self.bas = bas
        self.bah = bah
        self.total_income = (self.base + self.bas + self.bah)*12 + self.other_income
        self.taxable_income = self.base*12 + self.other_income
        self.compute_taxes()
        self.saved = self.total_income - self.fed_tax - self.state_tax - self.cost_of_living

    def __str__(self):
        return """{} at zip {}
base:\t${:.2f} bah:\t${:.2f} bas:\t${:.2f}
other income:\t${:.2f}
total income:\t${:.2f}
taxable income:\t${:.2f}
fed tax:\t${:.2f}
state tax:\t${:.2f}
cost of living:\t${:.2f}
saved:\t{}""".format(self.rank, self.zip_code, self.base, self.bah, self.bas, self.other_income,
                     self.total_income,self.taxable_income, self.fed_tax, self.state_tax,
                     self.cost_of_living,self.saved)

        #return """You make a total of ${0:.2f} a year.
#You pay ${1:.2f} in federal and ${2:.2f} in state taxes.
#Your cost of living is ${3:.2f} so you save ${4:.2f} annually ({5:.2f}%)""".format(
#    self.total_income, self.fed_tax, self.state_tax, self.cost_of_living, self.saved, self.saved*100/self.total_income)


class Account():
    def __init__(self, vals):
        self.name = vals["Type"]
        self.balance = vals["Balance"]
        self.proj_growth = vals["Growth Percent"]
        self.hasLimit = False
        self.this_year = 0

    def contribute(self, amount):
        self.balance += amount
        self.this_year += amount

    def reset_year(self):
        self.this_year = 0

    def monthly_grow(self):
        self.balance *= (1 + (self.proj_growth/1200))

    def gets_match(self):
        return self.name == "TSP"

    def __str__(self):
        return """{} account has a balance of ${:.2f} and a projected growth rate of {}%. ${:.2f} of contributions have been made this year.""".format(
            self.name, self.balance, self.proj_growth, self.this_year)

class Retirement(Account):
    def __init__(self, vals, limit):
        super().__init__(vals)
        self.hasLimit = True
        self.limit = limit.iloc[0]

    def __str__(self):
        return super().__str__() + " Member's annual contribution limit is ${:.2f}.".format(self.limit)
