class GoogleCampaign:
    campaign_id=''
    campaign_name=''
    cost=0
    budget=0
    effectiveStatus=""

    def __init__(self, campaign_id, campaign_name, cost, budget, effectiveStatus):
        self.campaign_id = campaign_id
        self.campaign_name = campaign_name
        self.cost=cost
        self.budget=budget
        self.effectiveStatus=effectiveStatus

    def get_total_budget(self):
        total_budget=0
        if(self.effectiveStatus==2):
            total_budget+=self.budget
        return total_budget/1000000
    
    def get_total_cost(self):
        return self.cost/1000000





