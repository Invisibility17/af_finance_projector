import datetime
import numpy as np
class Member():
    def __init__(self, personal, tax_sheet):
        self.rank           = personal.loc["Rank", "Value"]
        self.EAD            = personal.loc["EAD", "Value"]
        self.compute_TIS(datetime.datetime.now())

        self.zip_code       = personal.loc["BAH location", "Value"]

        self.married        = personal.loc["Married?", "Value"].lower() == "yes"
        self.dependents     = personal.loc["Dependents?", "Value"].lower() == "yes"

        self.other_income   = personal.loc["Other income", "Value"]
        self.cost_of_living = personal.loc["Cost of Living", "Value"]
        self.state_tax      = personal.loc["State Tax", "Value"]
        self.BRS            = personal.loc["BRS", "Value"].lower() == "yes"
        self.total_income = 1
        self.fed_tax =1
        self.saved = 1
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

    def compute_TIS(self, when):
        # probably bounds the leap day error
        self.time_in_service = when-self.EAD
        if self.time_in_service < datetime.timedelta(days=2*365.2425):
            self.senority = 1
        elif self.time_in_service < datetime.timedelta(days=3*365.2425):
            self.senority = 2
        elif self.time_in_service < datetime.timedelta(days=4*365.2425):
            self.senority = 3
        elif self.time_in_service < datetime.timedelta(days=6*365.2425):
            self.senority = 4
        elif self.time_in_service < datetime.timedelta(days=8*365.2425):
            self.senority = 5
        elif self.time_in_service < datetime.timedelta(days=10*365.2425):
            self.senority = 6
        elif self.time_in_service < datetime.timedelta(days=12*365.2425):
            self.senority = 7
        elif self.time_in_service < datetime.timedelta(days=14*365.2425):
            self.senority = 8
        elif self.time_in_service < datetime.timedelta(days=16*365.2425):
            self.senority = 9
        elif self.time_in_service < datetime.timedelta(days=18*365.2425):
            self.senority = 10
        elif self.time_in_service < datetime.timedelta(days=20*365.2425):
            self.senority = 11
        elif self.time_in_service < datetime.timedelta(days=22*365.2425):
            self.senority = 12
        elif self.time_in_service < datetime.timedelta(days=24*365.2425):
            self.senority = 13
        elif self.time_in_service < datetime.timedelta(days=26*365.2425):
            self.senority = 14
        elif self.time_in_service < datetime.timedelta(days=28*365.2425):
            self.senority = 15
        elif self.time_in_service < datetime.timedelta(days=30*365.2425):
            self.senority = 16
        elif self.time_in_service < datetime.timedelta(days=32*365.2425):
            self.senority = 17
        elif self.time_in_service < datetime.timedelta(days=34*365.2425):
            self.senority = 18
        elif self.time_in_service < datetime.timedelta(days=36*365.2425):
            self.senority = 19
        elif self.time_in_service < datetime.timedelta(days=38*365.2425):
            self.senority = 20
        elif self.time_in_service < datetime.timedelta(days=40*365.2425):
            self.senority = 21
        else:
            self.senority = 22
        return self.senority

    def life_change(self, change_matrix): #promotion_info=None, move_info=None, family_info=None):
        change_matrix = change_matrix.sort_values(by=["Time"])
        print(change_matrix)
        # Data Frame:
        #           Time Base BAH BAS Married Dependents
        # Promote
        # Move
        # Marry
        # Kid
        
        # promotion: affects base, bah, bas (+taxes, saved)
        time = promotion_info.loc["Promote", "Time"]
        if not np.isnan(time):
            time = time.month

        # move: affects bah (+saved)

        # marriage: affects bah (+taxes, saved)

    #def promote(self, rank=self.rank, time, new_base=self.base, new_bah=self.bah, new_bas=self.bas):
    #   pass
        # compute total income
        # compute taxable income
        #self.total_income = (self.base + self.new_bah )* time.month +  
    
    def update_income(self, new_extra_income):
        self.other_income = new_extra_income
        self.total_income = (self.base + self.bah + self.bas)*12 + self.other_income
        self.taxable_income = self.base*12 + self.other_income
        self.compute_taxes()
        self.saved = self.total_income - self.fed_tax - self.state_tax - self.cost_of_living

    def update_COL(self, new_col):
        self.cost_of_living = new_col
        self.saved = self.total_income - self.fed_tax - self.state_tax - self.cost_of_living

    def move(self, time, new_zip, new_bah):
        pass
        
        
    
    #def update_family(self, time, married=self.married, dependents=self.married,
    #                  new_bah=self.bah, new_state=self.state_tax):
    #    if new_bah != self.bah:
    #        pass
            
        
    
    def new_year(self, year):
        self.compute_TIS(year)
        self.total_income = (self.base + self.bas + self.bah)*12 + self.other_income
        self.taxable_income = self.base * 12 + self.other_income
        
    def set_pay_allowances(self, base, bas, bah):
        self.base = base 
        self.bas = bas
        self.bah = bah
        self.total_income = (self.base + self.bas + self.bah)*12 + self.other_income
        self.taxable_income = self.base*12 + self.other_income
        self.compute_taxes()
        self.saved = self.total_income - self.fed_tax - self.state_tax - self.cost_of_living

    def __str__(self):
        return """You make a total of ${0:.2f} a year.
You pay ${1:.2f} in federal and ${2:.2f} in state taxes.
Your cost of living is ${3:.2f} so you save ${4:.2f} annually ({5:.2f}%)""".format(
    self.total_income, self.fed_tax, self.state_tax, self.cost_of_living, self.saved, self.saved*100/self.total_income)


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
