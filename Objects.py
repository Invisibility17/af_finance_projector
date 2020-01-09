import datetime
class Member():
    def __init__(self, vals):
        self.rank           = vals.loc["Rank", "Value"]
        self.EAD            = vals.loc["EAD", "Value"]
        self.zip_code       = vals.loc["BAH location", "Value"]
        self.married        = vals.loc["Married?", "Value"].lower() == "yes"
        self.dependents     = vals.loc["Dependents?", "Value"].lower() == "yes"
        self.other_income   = vals.loc["Other income", "Value"]
        self.cost_of_living = vals.loc["Cost of Living", "Value"]
        self.state_tax      = vals.loc["State Tax", "Value"]
        self.BRS            = vals.loc["BRS", "Value"].lower() == "yes"
        self.compute_TIS(datetime.datetime.now())

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

    def promote(self, rank, time, new_base, new_bah):
        pass
        #self.total_income = (self.base + self.new_bah )* time.month +  

    def update_costs(self, fed):
        pass
    
    def update_income(self, new_extra_income):
        pass
    
    def update_family(self, married, dependents, new_bah, new_fed, new_state):
        pass
    
    def new_year(self, year):
        self.compute_TIS(year)
        self.total_income = (self.base + self.bas + self.bah)*12 + self.other_income
        self.taxable_income = self.base * 12 + self.other_income

    """def update_prorated(self, rank=self.rank, time=datetime.datetime.now().year,
               new_base=self.base, new_bah=self.bah, new_fed=self.fed_tax):
        self.rank = rank
        self.compute_TIS(time)

        if self.bah != 
        self.total_income = self.bas * 12 + 
        self.base = 
        self.bah = new_bah
        self.fed_tax = new_fed"""
        
    def set_secondary(self, base, bas, bah, fed):
        self.base = base 
        self.bas = bas
        self.bah = bah
        self.fed_tax = fed
        self.total_income = (self.base + self.bas + self.bah)*12 + self.other_income
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
