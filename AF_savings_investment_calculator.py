#import xlrd
#import csv
import tabula
import pandas
from os.path import exists
import datetime
import numpy
from Objects import Member

class Account():
    def __init__(self, vals):
        self.name = vals[0]
        self.balance = vals[1]
        self.proj_growth = vals[2]

    def __str__(self):
        return """{} account has a balance of ${:.2f} and a projected growth rate of {}%""".format(
            self.name, self.balance, self.proj_growth)

class TSP(Account):
    pass

class IRA(Account):
    def contribute(self, amount):
        pass
            
def main():
    # Stage 1: initialize member for current / past year
    me = pull_member("Rachel_money.xlsx")
    base_pay = pull_base_pay("2020 Military Pay_Basic_DP.pdf", "pay_chart.csv", me.senority, me.rank)
    bas = pull_bas("Air_Force_money.xlsx", me.rank)
    bah = pull_bah("BAH", me.zip_code, me.rank, me.dependents)
    fed_tax = pull_taxes("Air_Force_money.xlsx", base_pay*12+me.other_income, me.married)
    me.set_secondary(base_pay*12, bas*12, bah*12, fed_tax)
    #print(me)

    # Stage 2: initialize assets for current year
    assets = pull_assets("Rachel_money.xlsx")

    # Stage 3: see if projections exist for years ahead.
    projection = pull_projection("Rachel_money.xlsx")

    # Stage 4: create and output projections
    now_year = datetime.datetime.now().year
    for row in range(projection.shape[0]):
        this_proj = projection.iloc[row,:]
        for year in range(now_year, this_proj["Year"], 1):
            print(year)

        now_year = this_proj["Year"]+1

def pull_projection(member_sheet):
    proj_sheet = read_sheet(member_sheet, "Career Projection")
    return proj_sheet
    
def pull_assets(member_sheet):
    asset_sheet = read_sheet(member_sheet, "Assets")
    accounts = []
    for r in range(asset_sheet.shape[0]):
        if "TSP" in asset_sheet.iloc[r,0]:
            accounts.append(TSP(asset_sheet.iloc[r,:]))
        elif "IRA" in asset_sheet.iloc[r,0]:
            accounts.append(IRA(asset_sheet.iloc[r,:]))
        else:
            accounts.append(Account(asset_sheet.iloc[r,:]))
    return accounts
    
def pull_member(member_sheet):
    career_stats = read_sheet(member_sheet, "Career Stats")
    me = Member(career_stats.iloc[:,1])
    return me

def pull_taxes(money_sheet, annual_base_pay, married):
    # Pull in rates, brackets, etc.
    tax_sheet = read_sheet(money_sheet, "Tax Brackets")
    rates = tax_sheet.loc[:,"Tax Rate"]
    if married:
        brackets = tax_sheet.loc[:,"Married"]
        deduction = tax_sheet.loc[0,"Standard Married Deduction"]
    else:
        brackets = tax_sheet.loc[:,"Single"]
        deduction = tax_sheet.loc[0,"Standard Single Deduction"]

    # Calculate FICA taxes
    fica_ceiling = tax_sheet.loc[0,"FICA Ceiling"]
    fica_rate = tax_sheet.loc[0,"FICA Rate"]
    if annual_base_pay > fica_ceiling:
        total_tax = float((fica_ceiling * fica_rate)/100)
    else:
        total_tax = float((annual_base_pay * fica_rate)/100)

    # Subtract standard deduction and calculate federal taxes
    annual_base_pay -= deduction
    total_tax += annual_base_pay * (rates[0] / 100)
    for i in range(1, len(rates), 1):
        if annual_base_pay > brackets[i-1]:
            total_tax += (annual_base_pay - brackets[i-1])*(rates[i]-rates[i-1])/100
        else:
            break
    
    return total_tax

    
def pull_bas(BAS_sheet, rank):
    BAS_sheet = read_sheet(BAS_sheet, "BAS")
    if "O" in rank:
        return BAS_sheet.iloc[0, 1]
    else:
        return BAS_sheet.iloc[1,1]

def pull_base_pay(base_pdf, base_csv, my_senority, my_rank):
    if not exists(base_csv):
        tabula.convert_into(base_pdf, base_csv)
    base_sheet = read_sheet(base_csv, base_csv.split(".")[0])
    senority_col = base_sheet.iloc[:,my_senority]
    ranks_col = base_sheet.iloc[:,0]
    for i,rank in enumerate(ranks_col):
        if my_rank in str(rank):
            base_pay = base_sheet.iloc[i,my_senority]
            if numpy.isnan(base_pay):
                base_pay = base_sheet.iloc[i+1, my_senority]
            break
    return base_pay

def read_sheet(file_name, sheet_name):
    if file_name.split(".")[1] == "xlsx":
        return pandas.read_excel(file_name, sheet_name)
    elif file_name.split(".")[1] == "csv":
        return pandas.read_csv(file_name)

def pull_bah(folder, zip_code, rank, dependents):
    with open(folder+"\\sorted_zipmha20.txt", "r") as f:
        for line in f:
            if str(zip_code) in line:
                area = line.split()[1]

    if rank[0].upper() == "E":
        index = int(rank[-1])
    elif rank[0].upper() == "W":
        index = int(rank[-1]) + 9
    elif rank[-1].upper() == "E":
        index = int(rank[-2]) + 14
    else:
        index = int(rank[-1]) + 17

    if dependents:
        with open(folder + "\\bahw20.txt", "r") as f:
            for line in f:
                if area in line:
                    return float(line.split(",")[index])
    else:
        with open(folder + "\\bahwo20.txt", "r") as f:
            for line in f:
                if area in line:
                    return float(line.split(",")[index])

main()
