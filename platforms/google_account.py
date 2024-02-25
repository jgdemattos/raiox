from datetime import datetime
from datetime import date
from calendar import monthrange

class GoogleAccount:
    account_id=''
    campaigns=[]

    def __init__(self, account_id):
        self.account_id = account_id
        self.campaigns=[]

    def set_google_campaigns(self, campaigns):
        for  campaign in campaigns:
            self.campaigns.append(campaign)
    
    def get_total_budget(self):
        total_budget=0
        for campaign in self.campaigns:
            if(campaign.effectiveStatus==2):
                total_budget+=campaign.get_total_budget()
        return total_budget

    def get_total_cost(self):
        total_cost=0
        for campaign in self.campaigns:
            total_cost+=campaign.get_total_cost()
        return total_cost

    def calculate_spend_projection(self):
        today = date.today()
        last_day_this_month=monthrange(today.year, today.month)[1]

        days_left_this_month=((date(today.year, today.month, today.day) - date(today.year, today.month, last_day_this_month)).days)*-1
        total_spend_projected=0

        account_budget=0
        account_cost=0
        for campaign in self.campaigns:
            account_budget+=campaign.get_total_budget()
            account_cost+=campaign.cost

        total_spend_projected=account_cost+(account_budget*days_left_this_month)

        return {
            "account_budget":account_budget/1000000,
            "account_cost":account_cost/1000000,
            "total_spend_projected":total_spend_projected/1000000
        }


