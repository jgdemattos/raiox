class MetaCampaign:
    daily_results=[]
    spend=0
    adsets=[]
    id=""
    name=""
    cbo=False
    budget=0
    effectiveStatus=""
    
    def __init__(self, id, name):
        self.id = id
        self.name = name
        self.adsets=[]
        self.effectiveStatus=""
        self.budget=0
        self.cbo=False
        self.spend=0

    def setEffectiveStatus(self,effectiveStatus):
        self.effectiveStatus=effectiveStatus

    def add_spend(self,spend):
        self.spend+=spend

    def set_budget(self,budget,cbo=False):
        self.cbo=cbo
        self.budget=budget
    
    def get_budget(self):
        if(self.cbo):
            return self.budget
        else:
            return self.get_total_budget()

    def add_investment(self,spend,date):
        updated_daily_result=[]
        existing_daily_result={}
        for daily_result in self.daily_results:
            if(date in daily_result and date==daily_result['date']):
                existing_daily_result=daily_result
                existing_daily_result['spend']=spend
            else:
                updated_daily_result.append(daily_result)
        
        if('date' in existing_daily_result):
            updated_daily_result.append(existing_daily_result)
        else:
            updated_daily_result.append({'date':date,'spend':float(spend)})

        self.daily_results=updated_daily_result

    def get_total_spend_from_daily(self):
        total_spend=0
        for daily_result in self.daily_results:
            total_spend+=daily_result['spend']
        return total_spend
    
    def get_total_spend(self):
        total_spend=0
        for adset in self.adsets:
            total_spend+=adset.spend
        return total_spend
    
    def get_linear_projection(self,days_left_this_month):
        total_spend_projected=0
        for adset in self.adsets:
            total_spend_projected+=adset.spend
        total_spend_projected=total_spend_projected+self.get_budget()*days_left_this_month
        return total_spend_projected

    def get_total_budget(self):
        total_budget=0
        print(f"{self.name} +++++++++ {self.cbo}")
        if(self.cbo):
            print(f"{self.name} === {self.budget}")
            total_budget=self.budget
        else:
            for adset in self.adsets:
                if(adset.effectiveStatus=="ACTIVE"):
                    total_budget+=adset.budget
        return total_budget
