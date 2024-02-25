class MetaAdset:
    id=""
    name=""
    campaign_id=""
    campaign_name=""
    budget=0
    spend=0
    effectiveStatus=""

    def __init__(self, id, name,campaign_id,campaign_name):
        self.id = id
        self.name = name
        self.campaign_id = campaign_id
        self.campaign_name = campaign_name
        self.spend=0
        self.budget=0
        self.effectiveStatus=""
    
    def set_budget(self,budget):
        self.budget=budget

    def add_spend(self,spend):
        self.spend+=spend

    def setEffectiveStatus(self,effectiveStatus):
        self.effectiveStatus=effectiveStatus