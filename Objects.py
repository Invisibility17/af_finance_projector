import datetime
class Member():
    def __init__(self, vals):
        self.rank = vals[0]
        self.EAD = vals[1]
        self.zip_code = vals[2]
        self.married = vals[3].lower() == "yes"
        self.dependents = vals[4].lower() == "yes"
        self.other_income = vals[5]
        self.cost_of_living = vals[6]
        self.state_tax = vals[7]
        self.BRS = vals[8].lower() == "yes"
        self.compute_TIS()

    def compute_TIS(self):
        # probably bounds the leap day error
        self.time_in_service = datetime.datetime.now()-self.EAD
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

    def set_secondary(self, base, bas, bah, fed):
        self.base = base 
        self.bas = bas
        self.bah = bah
        self.fed_tax = fed
        self.total_income = self.base + self.bas + self.bah + self.other_income
        self.saved = self.total_income - self.fed_tax - self.state_tax - self.cost_of_living

    def __str__(self):
        return """You make a total of ${0:.2f} a year.
You pay ${1:.2f} in federal and ${2:.2f} in state taxes.
Your cost of living is ${3:.2f} so you save ${4:.2f} annually ({5:.2f}%)""".format(
    self.total_income, self.fed_tax, self.state_tax, self.cost_of_living, self.saved, self.saved*100/self.total_income)
