from datetime import date
from datetime import datetime
from calendar import monthrange

class MessageBuilder:
    client_name=''
    channel_id=""
    businessmanagers=[]
    google_accounts=[]
    CANAL_SLACK="C05TGRE3C3Y"


    def __init__(self, client_name, channel_id):
        self.client_name = client_name
        self.channel_id=channel_id
        self.businessmanagers=[]
        self.google_accounts=[]

    def count_meta_adaccounts(self):
        number_adaccounts=0
        for  businessmanager in self.businessmanagers:
            for adaccount in businessmanager.adaccounts:
                number_adaccounts=number_adaccounts+1
        return number_adaccounts

    def count_meta_campaigns(self):
        number_campaigns=0
        for  businessmanager in self.businessmanagers:
            for adaccount in businessmanager.adaccounts:
                for camapign in adaccount.campaigns:
                    number_campaigns=number_campaigns+1
        return number_campaigns

    def count_google_campaigns(self):
        number_campaigns=0
        for  adaccount in self.google_accounts:
            for campaign in adaccount.campaigns:
                if(campaign.effectiveStatus==2):
                    number_campaigns=number_campaigns+1
        return number_campaigns

    def set_businessmanagers(self, businessmanagers):
        for  businessmanager in businessmanagers:
            self.businessmanagers.append(businessmanager)

    def set_google_accounts(self, google_accounts):
        for  google_account in google_accounts:
            self.google_accounts.append(google_account)

    def calculate_total_projection(self):
        absolute_total_spend=0
        absolute_total_budget=0

        for businessmanager in self.businessmanagers:
            absolute_total_spend=absolute_total_spend+businessmanager.calculate_total_spend()
            absolute_total_budget=absolute_total_budget+businessmanager.calculate_total_budget()

        for google_account in self.google_accounts:
            absolute_total_spend=absolute_total_spend+google_account.get_total_cost()
            absolute_total_budget=absolute_total_budget+google_account.get_total_budget()  

        today = date.today()
        last_day_this_month=monthrange(today.year, today.month)[1]

        days_left_this_month=((date(today.year, today.month, today.day) - date(today.year, today.month, last_day_this_month)).days)*-1
        total_spend_projected=0


        total_spend_projected=absolute_total_spend+(absolute_total_budget*days_left_this_month)

        return {
            "account_budget":"{:.2f}".format(float(absolute_total_budget)),
            "account_cost":"{:.2f}".format(float(absolute_total_spend)),
            "total_spend_projected":"{:.2f}".format(float(total_spend_projected))
        }


    def build_message(self,in_channel):
        today_date=date.today().strftime("%d/%m/%y")
        if(len(self.google_accounts)==0 and len(self.businessmanagers)==0):
            message={ 
                    "channel": self.CANAL_SLACK,
                    "blocks": [
                                {
                                    "type": "divider"
                                },
                                {
                                    "type": "header",
                                    "text": {
                                        "type": "plain_text",
                                        "text": f"[🔴 Sem conta Google ou Meta configuradas para {self.client_name} - {today_date} 🍊]",
                                        "emoji": True
                                    }
                                },
                                {
                                    "type": "divider"
                                }
                            ]
                        }
            return message

        projection=self.calculate_total_projection()

        message={ 
                    "channel": self.CANAL_SLACK,
                    "blocks": [
                                {
                                    "type": "divider"
                                },
                                {
                                    "type": "header",
                                    "text": {
                                        "type": "plain_text",
                                        "text": f"[🍊 RAIO-X estrutural de {self.client_name} - {today_date} 🍊]",
                                        "emoji": True
                                    }
                                },
                                {
                                    "type": "section",
                                    "fields": [
                                        {
                                            "type": "plain_text",
                                            "text": f"👥 Orçamento diário: R$ {projection['account_budget']};",
                                            "emoji": True
                                        },
                                        {
                                            "type": "plain_text",
                                            "text": f"💸 Total investido: R$ {projection['account_cost']};",
                                            "emoji": True
                                        },
                                        {
                                            "type": "plain_text",
                                            "text": f"📈 Projeção mês: R$ {projection['total_spend_projected']};",
                                            "emoji": True
                                        },
                                    ]
                                },
                                {
                                    "type": "divider"
                                }
                            ]
                        }
        if(len(self.businessmanagers)==0):
            message['blocks'].append({
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "[🔴 Sem contas Meta configuradas]",
                    "emoji": True
                }
            })
        else:
            message['blocks'].append({
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "[Meta Ads]",
                    "emoji": True
                }
            })
            message['blocks'].append({
                    "type": "divider"
            })

            message['blocks'].append({
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"{len(self.businessmanagers)} Business Managers monitorados:",
                    "emoji": True
                }
            })
            for bm in self.businessmanagers:                                
                message['blocks'].append({
                    "type": "section",
                    "text": {
                            "type": "plain_text",
                            "text": f"➡️ {bm.meta_businessmanager_name}",
                            "emoji": True
                        }
                })
                total_spend=float("{:.2f}".format(float(bm.calculate_total_spend())))
                total_budget=float("{:.2f}".format(float(bm.calculate_total_budget())))
                message['blocks'].append({
                    "type": "context",
                    "elements": [{
                                    "type": "plain_text",
                                    "text": f"💸 Total investido: R$ {total_spend}",
                                    "emoji": True
                                },
                                {
                                    "type": "plain_text",
                                    "text": f"💰 Orçamento atual: R$ {total_budget}",
                                    "emoji": True
                                }]
                })

            message['blocks'].append({
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"{self.count_meta_adaccounts()} Contas de Anúncio:",
                    "emoji": True
                }
            })    
            for bm in self.businessmanagers:
                for adaccount in bm.adaccounts:
                    message['blocks'].append({
                    "type": "section",
                    "text": {
                            "type": "plain_text",
                            "text": f"➡️ {adaccount.name} - {len(adaccount.campaigns)} Campanhas",
                            "emoji": True
                        }
                    })
                    total_spend=float("{:.2f}".format(float(adaccount.get_total_spend())))
                    total_budget="{:.2f}".format(float(adaccount.get_total_budget()))
                    message['blocks'].append({
                        "type": "context",
                        "elements": [{
                                        "type": "plain_text",
                                        "text": f"💸 Total investido: R$ {total_spend}",
                                        "emoji": True
                                    },
                                    {
                                        "type": "plain_text",
                                        "text": f"💰 Orçamento atual: R$ {total_budget}",
                                        "emoji": True
                                    }]
                    })
                    campaigns_list=""
                    for campaign in adaccount.campaigns:
                        campaign_total_spend=float("{:.2f}".format(float(campaign.get_total_spend())))
                        campaign_total_budget=float("{:.2f}".format(float(campaign.get_total_budget())))
                        if campaign.effectiveStatus=="ACTIVE":
                            status="🟢: ATIVA"
                        else:
                            status="🔴: PAUSADA"
                            
                        campaigns_list=campaigns_list+f"➡️ {campaign.name} \n 💸: R$ {campaign_total_spend} - 💰: R$ {campaign_total_budget} - {status} \n\n"

                    if campaigns_list=="":
                        campaigns_list="sem campanhas"
                    message['blocks'].append({
                                "type": "rich_text",
                                "elements": [
                                    {
                                        "type": "rich_text_preformatted",
                                        "elements": [
                                            {
                                                "type": "text",
                                                "text": campaigns_list
                                            }
                                        ]
                                    }
                                ]
                            })


            #################################3333333333333333333333333333333333333333333333333333333333333333333
        if(len(self.google_accounts)==0):
            message['blocks'].append({
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "[🔴 Sem contas Google configuradas]",
                    "emoji": True
                }
            })
        else:
            message['blocks'].append({
                    "type": "divider"
            })
            message['blocks'].append({
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "[Google Ads]",
                    "emoji": True
                }
            })
            message['blocks'].append({
                    "type": "divider"
            })
            message['blocks'].append({
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"{len(self.google_accounts)} contas Google:",
                    "emoji": True
                }
            })
            for account in self.google_accounts:
                message['blocks'].append({
                    "type": "section",
                    "text": {
                            "type": "plain_text",
                                    "text": f"➡️ {account.account_id} - {self.count_google_campaigns()} Campanhas",
                            "emoji": True
                        }
                })
                total_spend=float("{:.2f}".format(float(account.get_total_cost())))
                message['blocks'].append({
                    "type": "context",
                    "elements": [{
                                    "type": "plain_text",
                                    "text": f"💸 Total investido: R$ {total_spend}",
                                    "emoji": True
                                },
                                {
                                    "type": "plain_text",
                                    "text": f"💰 Orçamento atual: R$ {account.get_total_budget()}",
                                    "emoji": True
                                }]
                })
                campaigns_list=""
                for campaign in account.campaigns:
                    if(campaign.effectiveStatus==2):
                        campaign_total_spend=float("{:.2f}".format(float(campaign.get_total_cost())))
                        campaign_total_budget=float("{:.2f}".format(float(campaign.get_total_budget())))
                        campaigns_list=campaigns_list+f"➡️ {campaign.campaign_name} \n 💸: R$ {campaign_total_spend} 💰: R$ {campaign_total_budget} \n\n"

                if campaigns_list=="":
                    campaigns_list="sem campanhas"
                message['blocks'].append({
                            "type": "rich_text",
                            "elements": [
                                {
                                    "type": "rich_text_preformatted",
                                    "elements": [
                                        {
                                            "type": "text",
                                            "text": campaigns_list
                                        }
                                    ]
                                }
                            ]
                        })

        if(in_channel):
            message['response_type']="in_channel"
            
        return message