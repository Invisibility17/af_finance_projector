import tabula
import pandas
from os.path import exists
import datetime
import numpy as np
from Objects import Member, Account, Retirement
            
def main():
    misc_xls = "Air_Force_money.xlsx"
    me_xls = "member_profile.xlsx"
    pay_csv = "pay_chart.csv"
    
    # Stage 1: initialize member for current / past year
    taxes = read_sheet(misc_xls, "Tax Brackets")
    me, final_year = pull_member(me_xls, taxes)
    
    base_sheet = pull_base("2020 Military Pay_Basic_DP.pdf", pay_csv)
    base = calculate_base(base_sheet, me.senority, me.rank)
    
    bas_sheet = read_sheet(misc_xls, "BAS")
    bas = calculate_bas(bas_sheet, me.rank)
    
    bah = pull_bah("BAH", me.zip_code, me.rank, me.dependents)
    me.set_pay_allowances(base, bas, bah)
    
    # Stage 2: initialize assets for current year
    assets = pull_assets(me_xls, misc_xls)

    # Stage 3: see if projections exist for years ahead.
    raw_projections = read_sheet(me_xls, "Career Projection")
    projections = pull_projection(raw_projections, me, final_year, base_sheet, bas_sheet)

    # Stage 4: create and output projections
    this_year = datetime.datetime.now().year
    start_month = datetime.datetime.now().month + 1
    writer = pandas.ExcelWriter('member_summary.xlsx', engine='xlsxwriter')
    for proj in projections: # starts with this year
        saved = me.life_change(proj) # update member. Returns saved.
        year = proj.iloc[0,0].year
        if year == this_year:
            increment_accounts_partial_year(me, assets, start_month)
        else:
            increment_accounts_whole_year(me, assets)
        # Write results per year
        print(proj.iloc[0,0].year)
        print(me)
        total_assets = 0
        total_debts = 0
        account_summary = []
        for account in assets:
            print(account)
            account_summary.append([account.name, account.balance,
                                    account.this_year, account.contributions])
            total_assets += account.balance
            account.reset_year()
        account_summary = pandas.DataFrame(
            account_summary, columns = ["Account", "Balance",
                                        "Contributed This Year",
                                        "Total Contributions"])
        net_worth = total_assets - total_debts
        summary = [["Net Worth", net_worth], ["Assets", total_assets], ["Debts", total_debts]]
        summary = pandas.DataFrame(summary, columns=["Summary", "Dollars"])

        profit_loss = [["Income", me.total_income, 100],
                       ["Taxes", me.fed_tax + me.state_tax, (me.fed_tax + me.state_tax)*100/me.total_income],
                       ["Spent", me.cost_of_living, me.cost_of_living*100/me.total_income],
                       ["Saved", me.saved, me.saved*100/me.total_income]]
        profit_loss = pandas.DataFrame(profit_loss,
                                       columns = ["", "Absolute", "Percent"])
        
        summary.to_excel(writer, sheet_name = str(year), index=False)
        account_summary.to_excel(writer, sheet_name = str(year), startrow = 6, index=False)
        profit_loss.to_excel(writer, sheet_name = str(year), startcol=3, index=False)

    writer.save()
        
        
    
    
        

def increment_accounts_partial_year(me, assets, start_month):
    remain_to_save = me.saved 
    monthly_saves = [0]*len(assets)
    for i, account in enumerate(assets):
        if account.hasLimit and remain_to_save > (13 - start_month)*account.limit/12:
            monthly_saves[i] = account.limit / 12
            remain_to_save -= account.limit 
        else:
            monthly_saves[i] = remain_to_save/12
            remain_to_save = 0
            break

    for i in range(len(monthly_saves)):
        if assets[i].gets_match():
            govt_match = calculate_govt_match(me, monthly_saves[i])
        else:
            govt_match = 0
        for month in range(start_month, 13, 1):
            assets[i].contribute(monthly_saves[i] + govt_match)
            assets[i].monthly_grow()
    

    
def increment_accounts_whole_year(me, assets):
    remain_to_save = me.saved
    # In order of priority, max out accounts (accounting for government match), add to accounts, and account for growth
    monthly_saves = [0]*len(assets)
    for i, account in enumerate(assets):
        if account.hasLimit and remain_to_save > account.limit:
            monthly_saves[i] = account.limit / 12
            remain_to_save -= account.limit
        else:
            monthly_saves[i] = remain_to_save/12
            remain_to_save = 0
            break

    for i, asset in enumerate(assets):
        #account.contribute(monthly_saves)
        if asset.gets_match():
            govt_match = calculate_govt_match(me, monthly_saves[i])
        else:
            govt_match = 0
        for month in range(12):
            asset.contribute(monthly_saves[i] + govt_match)
            asset.monthly_grow()
    

def calculate_govt_match(me, monthly_amount):
    percent = monthly_amount / (me.matchable_income / 12) # this is a simplifying assumption
    if me.BRS:
        if percent >= 0.05:
            return (me.matchable_income/12) * .05
        elif percent >= 0.03:
            return (me.matchable_income/12) * .03 + ((percent - .03 ) * .5 * me.base_pay)
        else:
            return max(me.matchable_income * percent, me.matchable_income * .01)
    else:
        return 0
    
def pull_projection(raw, me, final_year, pay_chart, bas_chart):
    # get all the events

    promotions = raw.loc[:,["Promote Date", "New Rank"]]
    moves = raw.loc[:,["Move Date", "New Zip"]]
    marry = raw.loc[:,["Anniversary"]]
    kids = raw.loc[:,["Kid Birth Date"]]
    misc = raw.loc[:,["Other Date", "Cost of Living", "State Taxes", "Additional Income"]]
    events = []
    # put them in order -- time, type, data
    max_year = 0
    for row in promotions.iterrows():
        if not pandas.isnull(row[1]["Promote Date"]):
            if row[1]["Promote Date"].year > max_year:
                max_year = row[1]["Promote Date"].year
            events.append([row[1]["Promote Date"], "Promote", row[1]["New Rank"]])
    for row in moves.iterrows():
        if not pandas.isnull(row[1]["Move Date"]):
            if row[1]["Move Date"].year > max_year:
                max_year = row[1]["Move Date"].year
            events.append([row[1]["Move Date"], "Move", row[1]["New Zip"]])
    for row in marry.iterrows():
        if not pandas.isnull(row[1]["Anniversary"]):
            if row[1]["Anniversary"].year > max_year:
                max_year = row[1]["Anniversary"].year
            events.append([row[1]["Anniversary"], "Marry", ""])
    for row in kids.iterrows():
        if not pandas.isnull(row[1]["Kid Birth Date"]):
            if row[1]["Kid Birth Date"].year > max_year:
                max_year = row[1]["Kid Birth Date"].year
            events.append([row[1]["Kid Birth Date"], "Kid", ""])
    for row in misc.iterrows():
        if not pandas.isnull(row[1]["Other Date"]):
            if row[1]["Other Date"].year > max_year:
                max_year = row[1]["Other Date"].year
            if not pandas.isnull(row[1]["Cost of Living"]):
                events.append([row[1]["Other Date"], "Cost of Living", row[1]["Cost of Living"]])
            if not pandas.isnull(row[1]["State Taxes"]):
                events.append([row[1]["Other Date"], "State Taxes", row[1]["State Taxes"]])
            if not pandas.isnull(row[1]["Additional Income"]):
                events.append([row[1]["Other Date"], "Other Income", row[1]["Additional Income"]])
    if len(events) == 0:
        return pandas.DataFrame(events, columns=["Time", "Type", "Data"])

    # Check senority every year
    for all_year in range(datetime.datetime.now().year, max(final_year, max_year)+1, 1):
        events.append([me.EAD.replace(year=all_year, day=me.EAD.day+1), "Senority", ""])
    events = pandas.DataFrame(events, columns=["Time", "Type", "Data"])
    events.sort_values(by="Time", inplace=True)
    events.reset_index(inplace=True, drop=True)
    
    
    # Create update frames
    year = events.loc[0, "Time"].year
    start_row = 0
    last_row = 0

    events = create_update_frame(events, me, pay_chart, bas_chart)
    batched_events = []
    
    for row in events.iterrows():
        if not row[1].loc["Time"].year == year:
            batched_events.append( events.iloc[start_row:last_row+1,:])
            start_row = row[0]
            last_row = row[0]
            year = row[1].loc["Time"].year
        else:
            last_row = row[0]
    batched_events.append(events.iloc[start_row:last_row+1, :])
        
    return batched_events

def create_update_frame(rows, me, pay_chart, bas_chart):
    easy_rows = []
    rank = me.rank
    zip_code = me.zip_code
    base = me.base
    bah = me.bah
    bas = me.bas
    married = me.married
    dependents = me.dependents
    other_income = me.other_income
    cost_of_living = me.cost_of_living
    state_tax = me.state_tax
    senority = me.senority
    
    for row in rows.iterrows():
        time = row[1]["Time"]
        senority = me.compute_TIS(time)
        if row[1]["Type"] == "Promote":
            rank = row[1]["Data"]
            base = calculate_base(pay_chart, senority, rank)
            bah = pull_bah("BAH", zip_code, rank, dependents)
            bas = calculate_bas(bas_chart, rank)
        if row[1]["Type"] == "Move":
            zip_code = int(row[1]["Data"])
            bah = pull_bah("BAH", zip_code, rank, dependents)
        if row[1]["Type"] == "Marry":
            married = True
            dependents = True
            bah = pull_bah("BAH", zip_code, rank, married)
        if row[1]["Type"] == "Kid":
            dependents = True
            bah = pull_bah("BAH", zip_code, rank, dependents)
        if row[1]["Type"] == "Cost of Living":
            cost_of_living = row[1]["Data"]
        if row[1]["Type"] == "State Taxes":
            state_tax = row[1]["Data"]
        if row[1]["Type"] == "Other Income":
            other_income = row[1]["Data"]
        if row[1]["Type"] == "Senority":
            base = calculate_base(pay_chart, senority, rank)

        easy_rows.append([time, rank, zip_code, base, bah, bas,
                          married, dependents, cost_of_living,
                          state_tax, other_income])
            
    easy_frame = pandas.DataFrame(easy_rows, columns = ["Time", "Rank", "ZIP", "Base",
                                                        "BAH", "BAS", "Married",
                                                        "Dependents","Cost of Living",
                                                        "State Tax", "Other Income"])
    return easy_frame
    
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

    return accounts
    
def pull_member(member_sheet, taxes):
    career_stats = read_sheet(member_sheet, "Career Stats")
    career_stats = career_stats.set_index("Info")
    me = Member(career_stats, taxes)
    return me, career_stats.loc["Project Through", "Value"]

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
            if np.isnan(float(base_pay)):
                base_pay = base_sheet.iloc[i+1, my_senority]
            break
    return float(base_pay)

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
