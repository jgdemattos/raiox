from datetime import datetime
from datetime import date
from calendar import monthrange

class MetaAdaccount:
    id=''
    name=''
    owned=True
    campaigns=[]

    def __init__(self, id, name, owned=True):
        self.id = id
        self.name = name
        self.owned = owned
        self.campaigns=[]

    def set_campaigns(self,adsets):
        for adset in adsets:
            self.campaigns.append(adset)

    def get_total_budget(self):
        total_budget=0
        for campaign in self.campaigns:
            if(campaign.effectiveStatus=="ACTIVE"):
                total_budget+=campaign.get_total_budget()
        return total_budget
    
    def get_total_spend(self):
        total_spend=0
        for campaign in self.campaigns:
            total_spend+=campaign.get_total_spend()
        return total_spend 
    
    def calculate_spend_projection(self):
        #get days left in month
        today = date.today()
        last_day_this_month=monthrange(today.year, today.month)[1]
        days_left_this_month=((date(today.year, today.month, today.day) - date(today.year, today.month, last_day_this_month)).days)*-1

        total_budget=0
        total_current_spend=0
        total_spend_projected=0

        for campaign in self.campaigns:
            for adset in campaign.adsets:
                total_current_spend+=adset.spend

        #calculate total budgets with ACTIVE campaigns and adsets:
        for campaign in self.campaigns:
            if(campaign.effectiveStatus=="ACTIVE"):
                    total_budget+=campaign.get_budget()

        
        total_spend_projected+=total_current_spend+(total_budget*days_left_this_month)
        print(f"{total_current_spend}+({total_budget}*{days_left_this_month})")

        return(total_spend_projected)
    
    def is_in_this_list(self,id_list):
        formatted_ids_list=[]
        for id in id_list:
            formatted_ids_list.append("act_"+id)

        if(self.id in formatted_ids_list):
            return True
        else:
            return False
