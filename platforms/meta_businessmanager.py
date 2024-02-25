class MetaBusinessmanager:
    meta_businessmanager_name=''
    adaccounts=[]
    meta_businessmanager_id=''

    def __init__(self, meta_businessmanager_name,meta_businessmanager_id):
        self.meta_businessmanager_name = meta_businessmanager_name
        self.meta_businessmanager_id = meta_businessmanager_id
        self.adaccounts=[]

    def set_meta_businessmanager_name(self, name):
        self.meta_businessmanager_name=name

    def set_meta_adaccounts(self, adaccounts):
        for  adaccount in adaccounts:
            self.adaccounts.append(adaccount)

    def calculate_total_spend(self):
        total_spend=0
        for adaccount in self.adaccounts:
            total_spend=total_spend+adaccount.get_total_spend()

        return total_spend
    
    def calculate_total_budget(self):
        total_budget=0
        for adaccount in self.adaccounts:
            total_budget=total_budget+adaccount.get_total_budget()

        return total_budget


