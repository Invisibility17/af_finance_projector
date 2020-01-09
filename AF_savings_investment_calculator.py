#import xlrd
#import csv
import tabula
import pandas
from os.path import exists
import datetime
import numpy
from Objects import Member, Account, Retirement
            
def main():
    misc_xls = "Air_Force_money.xlsx"
    me_xls = "Rachel_money.xlsx"
    pay_csv = "pay_chart.csv"
    
    # Stage 1: initialize member for current / past year
    taxes = read_sheet(misc_xls, "Tax Brackets")
    me = pull_member(me_xls, taxes)
    
    base_sheet = pull_base("2020 Military Pay_Basic_DP.pdf", pay_csv)
    base = calculate_base(base_sheet, me.senority, me.rank)
    
    bas_sheet = read_sheet(misc_xls, "BAS")
    bas = calculate_bas(bas_sheet, me.rank)
    
    bah = pull_bah("BAH", me.zip_code, me.rank, me.dependents)
    print(me)
    #fed_tax = pull_taxes("Air_Force_money.xlsx", base_pay*12+me.other_income, me.married)
    #me.set_secondary(base_pay, bas, bah, fed_tax)
    
    # Stage 2: initialize assets for current year
    assets = pull_assets(me_xls, misc_xls)

    # Stage 3: see if projections exist for years ahead.
    raw_projections = read_sheet(me_xls, "Career Projection")
    projections = pull_projection(raw_projections, bas_sheet, base_sheet)

    # Stage 4: create and output projections
    """this_year = datetime.datetime.now().year
    index_year = this_year
    for row in range(projection.shape[0]):
        this_proj = projection.iloc[row,:]
        for year in range(index_year, this_proj["Year"], 1):
            # projection for gap rows / initial projection prior to further updates
            if year == this_year: # initial projection; do after current month only
                print("Calculating for remainder of current year: {}".format(year))
                increment_accounts_partial_year(me, assets, datetime.datetime.now().month+1)
            else: # gap rows; do entire year
                print("Calculating for future year: {}".format(year))
                increment_accounts_whole_year(me, assets)
            for a in assets:
                print(a)
        index_year = this_proj["Year"]+1
        
        # projection for current row
        # update all the January changes
        if not numpy.isnan(this_proj["Additional Income"]): 
            me.additional_income = this_proj["Additional Income"]
        if not numpy.isnan(this_proj["Zip Code"]): # all moves happen in January. Slightly inaccurate; account with CoL if necessary.
            me.zip_code = this_proj["Zip Code"]
        if not numpy.isnan(this_proj["Cost of Living"]):
            me.cost_of_living = this_proj["Cost of Living"]
        if not numpy.isnan(this_proj["State Taxes"]):
            me.state_tax = this_proj["State Taxes"]
        if not numpy.isnan(this_proj["Dependents"]):
            me.dependents = this_proj["Dependents"].lower() == "yes"
        if not numpy.isnan(this_proj["Married"]):
            me.dependents = this_proj["Married"].lower() == "yes"

        # Promote and calculate new seniority
        #if (not numpy.isnan(this_proj["Rank"])) and (this_proj["Rank"] != me.rank):
        #    pass
            
        if this_proj["Year"] == this_year:
            if datetime.datetime.now().month > me.EAD.month:
                pass
            # in early months, wait for promotion

            # update rank

            # proceed accordingly

        else:
            pass
       """
        

def increment_accounts_partial_year(me, assets, start_month):
    remain_to_save = (13 - start_month)*me.saved / 12
    monthly_saves = [0]*len(assets)
    for i, account in enumerate(assets):
        if account.hasLimit and remain_to_save > (13 - start_month)*account.limit/12:
            monthly_saves[i] = account.limit / (13-start_month)
            remain_to_save -= account.limit
        else:
            monthly_saves[i] = remain_to_save/(13-start_month)
            remain_to_save = 0
            break

    for i in range(len(monthly_saves)):
        #account.contribute(monthly_saves)
        if assets[i].gets_match():
            govt_match = calculate_govt_match(me, monthly_saves[i])
        for month in range(start_month, 13, 1):
            assets[i].contribute(monthly_saves[i] + govt_match)
            assets[i].monthly_grow()

    
def increment_accounts_whole_year(me, assets):
    # In order of priority, max out accounts (accounting for government match), add to accounts, and account for growth
    remain_to_save = me.saved
    monthly_saves = [0]*len(assets)
    for i, account in enumerate(assets):
        if account.hasLimit and remain_to_save > account.limit:
            monthly_saves[i] = account.limit / 12
            remain_to_save -= account.limit
        else:
            monthly_saves[i] = remain_to_save/12
            remain_to_save = 0
            break

    for i in range(len(monthly_saves)):
        #account.contribute(monthly_saves)
        if assets[i].gets_match():
            govt_match = calculate_govt_match(me, monthly_saves[i])
            for month in range(12):
                assets[i].contribute(monthly_saves[i] + govt_match)
                assets[i].monthly_grow()
    

def calculate_govt_match(me, monthly_amount):
    percent = monthly_amount / me.base
    if me.BRS:
        if percent >= 0.05:
            return me.base * .05
        elif percent >= 0.03:
            return me.base * .03 + ((percent - .03 ) * .5 * me.base_pay)
        else:
            return max(me.base * percent, me.base * .01)
    else:
        return 0
    
def pull_projection(raw, bas_chart, pay_chart):
    # get all the events

    promotions = raw.loc[:,["Promote Date", "Promote"]]
    moves = raw.loc[:,["Move Date", "Move"]]
    marry = raw.loc[:,"Anniversary"]
    kids = raw.loc[:,"Kid Birth Date"]
    misc = raw.loc[:,["Other Date", "Cost of Living", "State Taxes", "Additional Income"]]
    print(promotions)
    print(moves)
    print(marry)
    print(kids)
    print(misc)
    events = []
    # put them in order -- time, type, data
    for row in promotions.iterrows():
        print(row)
    """for row in range(promotions.shape[0]):
        events.append([promotions.loc[row, "Promote Date"], "Promote", promotions.low[row, "Promote"]])
    pprint(events)"""
    # combine any in the same year

    # put all in data frames

    # calculate / fill data frames for BAS, BAH, Base
    
    return promotions
    
def pull_assets(member_sheet, limit_sheet):
    limits = read_sheet(limit_sheet, "Contribution Limits")
    assets = read_sheet(member_sheet, "Assets")
    accounts = []
    for r in range(assets.shape[0]):
        if "TSP" in assets.loc[assets.index[r], "Type"]:
            accounts.append(Retirement(assets.iloc[r,:], limits.loc[:,"TSP"]))
        elif "IRA" in assets.loc[assets.index[r], "Type"]:
            accounts.append(Retirement(assets.iloc[r,:], limits.loc[:,"IRA"]))
        else:
            accounts.append(Account(assets.iloc[r,:]))
    for a in accounts:
        print(a)
    return accounts
    
def pull_member(member_sheet, taxes):
    career_stats = read_sheet(member_sheet, "Career Stats")
    career_stats = career_stats.set_index("Info")
    me = Member(career_stats, taxes)
    return me

def pull_taxes(money_sheet): #, annual_base_pay, married):
    # Pull in rates, brackets, etc.
    tax_sheet = read_sheet(money_sheet, "Tax Brackets")
    return tax_sheet
"""
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
    
    return total_tax"""

    
def calculate_bas(BAS_sheet, rank):
    if "O" in rank:
        return BAS_sheet.iloc[0, 1]
    else:
        return BAS_sheet.iloc[1,1]

def pull_base(base_pdf, base_csv):
    if not exists(base_csv):
        tabula.convert_into(base_pdf, base_csv)
    base_sheet = read_sheet(base_csv, base_csv.split(".")[0])
    return base_sheet

def calculate_base(base_sheet, my_senority, my_rank):
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
