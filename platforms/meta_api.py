import requests
import json
from datetime import datetime
from datetime import date
from calendar import monthrange
from meta_adset import MetaAdset
from meta_campaign import MetaCampaign
from meta_adaccount import MetaAdaccount

access_token="EABTkTFaTdZB4BO97oWYcvVZCaU6LZBKqoPXPyZALIcg4rOJVJBgRdaVgP3S2eZASZC1W4kReCxZCeIMh4dbMxWfNxO7Kr9MmZCmlqepDiMxcZCrOKi3woDXrnv0XYj69kUynlMWfxgpmbUsZAIagF41uZBnZBZBJcnfldHzJxNwkfGZB78UzZAmjMgi7zVvbMZBIzi8ZD";
monday_token='eyJhbGciOiJIUzI1NiJ9.eyJ0aWQiOjI1MzUzMTM3NywiYWFpIjoxMSwidWlkIjozNzQwOTk4NSwiaWFkIjoiMjAyMy0wNC0yOFQxODowNDozOS4wMDBaIiwicGVyIjoibWU6d3JpdGUiLCJhY3RpZCI6MTA1NzAyNjUsInJnbiI6InVzZTEifQ.k5lf_2ccOP9fiETIKwaHUha3HDSagT0Qxx7rKk08MWY'

def get_meta_adaccounts(meta_id):
    fields="fields=name,owned_ad_accounts{name},client_ad_accounts{name}"
    url=f'https://graph.facebook.com/v16.0/{meta_id}/?{fields}&access_token={access_token}'
    #print(url)
    ret = requests.get(url)
    meta_adaccounts_data=json.loads(ret.text)

    meta_adaccounts=create_meta_adaccounts(meta_adaccounts_data)

    return {'meta_businessmanager_name':meta_adaccounts_data['name'],'meta_adaccounts':meta_adaccounts}

def create_meta_adaccounts(meta_adaccounts_data):
    adaccounts=[]

    for meta_adaccount_data in meta_adaccounts_data['owned_ad_accounts']['data']:
        new_meta_adaccount=MetaAdaccount(meta_adaccount_data['id'],meta_adaccount_data['name'])
        adaccounts.append(new_meta_adaccount)
    if 'client_ad_accounts' in meta_adaccounts_data:
        for meta_adaccount_data in meta_adaccounts_data['client_ad_accounts']['data']:
            new_meta_adaccount=MetaAdaccount(meta_adaccount_data['id'], meta_adaccount_data['name'], False)
            adaccounts.append(new_meta_adaccount)

    return adaccounts

def get_meta_adsets(meta_adaccount):
    #get days left in month
    today = date.today()
    last_day_this_month=monthrange(today.year, today.month)[1]

    days_left_this_month=((date(today.year, today.month, today.day) - date(today.year, today.month, last_day_this_month)).days)*-1

    #request adsets from insights API per adset with spend data  
    timerange=f'{{"since":"{str(date(today.year, today.month, 1))}","until":"{str(date(today.year, today.month, today.day))}"}}'

    #https://graph.facebook.com/v16.0/act_484264493436412/insights?fields=campaign_name,adset_name,spend,campaign_id,adset_id&level=adset&time_increment=all_days&limit=150&time_range={%22since%22:%222023-06-01%22,%22until%22:%222023-06-12%22}&access_token=
    url=f'https://graph.facebook.com/v16.0/{meta_adaccount.id}/insights?fields=campaign_name,campaign_id,adset_name,adset_id,spend&level=adset&time_increment=all_days&limit=150&time_range={timerange}&access_token={access_token}'
    #print(url)
    meta_adset_data = requests.get(url)
    meta_adsets=get_all_adsets_from_insightsAPI(json.loads(meta_adset_data.text)["data"])

    return meta_adsets

def get_meta_campaigns(meta_adaccount, meta_adsets):

    meta_campaigns=[]
    for meta_adset in meta_adsets:
        if(not check_if_campaign_exists(meta_campaigns, meta_adset.campaign_id)):
            new_meta_campaign=MetaCampaign(meta_adset.campaign_id,meta_adset.campaign_name)
            meta_campaigns.append(new_meta_campaign)
    
    # add adsets to corresponding campaigns
    for meta_campaign in meta_campaigns:
        new_meta_adsets=[]
        for meta_adset in meta_adsets:
            if(meta_campaign.id==meta_adset.campaign_id):
                new_meta_adsets.append(meta_adset)
        meta_campaign.adsets=new_meta_adsets
    
    for meta_campaign in meta_campaigns:
        #request adset data from campaign API
        url=f'https://graph.facebook.com/v16.0/{meta_campaign.id}/?fields=start_time,stop_time,lifetime_budget,name,daily_budget,effective_status,adsets{{name,id,daily_budget,effective_status}}&limit=50&date_preset=this_month&access_token={access_token}'
        #print(url)
        ret = requests.get(url)
        meta_campaign_data=json.loads(ret.text)
        add_budget_from_adsetsAPI(meta_campaign_data,meta_campaigns)

    return meta_campaigns

def get_all_adsets_from_insightsAPI(adsets):
    all_adsets=[]

    for adset in adsets:

        new_adset = MetaAdset(adset['adset_id'],adset['adset_name'],adset['campaign_id'],adset['campaign_name'])
        if('spend' in adset):
            new_adset.add_spend(float(adset['spend']))
        all_adsets.append(new_adset)
    return all_adsets

def check_if_campaign_exists(campaigns,campaign_id):
    for campaign in campaigns:
        if(campaign_id==campaign.id):
            return True
    return False

def add_budget_from_adsetsAPI(insights_campaign,meta_campaigns):
    for meta_campaign in meta_campaigns:
        if(meta_campaign.id==insights_campaign['id']):
                meta_campaign.setEffectiveStatus(insights_campaign['effective_status'])
                #CBO ou impulsionado
                if 'daily_budget' in insights_campaign:
                    meta_campaign.set_budget(float("{:.2f}".format(float(insights_campaign['daily_budget'])/100.00)),True)
                    meta_campaign.cbo=True
                #campanha CBO com programacao nos conjuntos
                elif 'lifetime_budget' in insights_campaign: 
                    lifetime_budget=float("{:.2f}".format(float(insights_campaign['lifetime_budget'])/100.00))
                    start_time=datetime.fromisoformat(insights_campaign['start_time'])
                    stop_time=datetime.fromisoformat(insights_campaign['stop_time'])
                    days_campaign_duration=((datetime.date(start_time) - datetime.date(stop_time)).days)*-1
                    print(lifetime_budget)
                    print(days_campaign_duration)
                    print(lifetime_budget/days_campaign_duration)
                    meta_campaign.set_budget(lifetime_budget,True)
                    meta_campaign.cbo=True
                #campanha normal                
                else:
                    if 'adsets' in insights_campaign: 
                        for insights_adset in insights_campaign['adsets']['data']:
                            for meta_adset in meta_campaign.adsets:
                                if(meta_adset.id==insights_adset['id']):
                                    meta_adset.setEffectiveStatus(insights_adset['effective_status'])
                                    meta_adset.set_budget(float("{:.2f}".format(float(insights_adset['daily_budget'])/100.00)))

    return 'ok'

#######################################################################################################
#######################################################################################################
#######################################################################################################
#######################################################################################################
#######################################################################################################
def request_profile_BM_info(BM_id):
    fields="fields=owned_ad_accounts{name},client_ad_accounts{name}"
    url=f'https://graph.facebook.com/v16.0/{BM_id}/?{fields}&access_token={access_token}'
    print(url)
    ret = requests.get(url)
    BM_info=json.loads(ret.text)
    print(BM_info)
    return BM_info['owned_ad_accounts']['data']

def add_budget_to_adsets_from_ADSETS(insights_adsets,adsets):
    for adset in adsets:
        for insights_adset in insights_adsets:
            if(adset.id==insights_adset['id']):
                adset.set_budget(float(insights_adset['daily_budget']))

def request_budget_projection(BM_info,include_acts):
    #get days left in month
    today = date.today()
    last_day_this_month=monthrange(today.year, today.month)[1]

    days_left_this_month=((date(today.year, today.month, today.day) - date(today.year, today.month, last_day_this_month)).days)*-1

    total_budget=0
    total_current_spend=0
    total_spend_projected=0

    for account in BM_info:
        print(account["id"])
        print(include_acts)
        print(account["id"] not in include_acts)
        if(len(include_acts)>0):
            if account["id"] not in include_acts: continue
        #request adsets from insights API per adset with spend data  
        timerange=f'{{"since":"{str(date(today.year, today.month, 1))}","until":"{str(date(today.year, today.month, today.day))}"}}'
        #https://graph.facebook.com/v16.0/act_484264493436412/insights?fields=campaign_name,adset_name,spend,campaign_id,adset_id&level=adset&time_increment=all_days&limit=150&time_range={%22since%22:%222023-06-01%22,%22until%22:%222023-06-12%22}&access_token=
        url=f'https://graph.facebook.com/v16.0/{account["id"]}/insights?fields=campaign_name,campaign_id,adset_name,adset_id,spend&level=adset&time_increment=all_days&limit=150&time_range={timerange}&access_token={access_token}'
        print(url)
        adset_data = requests.get(url)
        adsets=get_all_adsets_from_insightsAPI(json.loads(adset_data.text)["data"])

        campaigns=[]
        for adset in adsets:
            if(not check_if_campaign_exists(campaigns, adset.campaign_id)):
                new_campaign=MetaCampaign(adset.campaign_id,adset.campaign_name)
                campaigns.append(new_campaign)

        # add adsets to corresponding campaigns
        for campaign in campaigns:
            new_adsets=[]
            for adset in adsets:
                if(campaign.id==adset.campaign_id):
                    new_adsets.append(adset)
            campaign.adsets=new_adsets

        for campaign in campaigns:
            #request adset data from campaign API
            url=f'https://graph.facebook.com/v16.0/{campaign.id}/?fields=start_time,stop_time,lifetime_budget,name,daily_budget,effective_status,adsets{{name,id,daily_budget,effective_status}}&limit=50&date_preset=this_month&access_token={access_token}'
            print(url)
            ret = requests.get(url)
            ret_campaign=json.loads(ret.text)
            add_budget_from_adsetsAPI(ret_campaign,campaigns)

        current_account_spend=0
        for adset in adsets:
            total_current_spend+=adset.spend
            current_account_spend+=adset.spend

        current_account_budget=0
        #calculate total budgets with ACTIVE campaigns and adsets:
        for campaign in campaigns:
            if(campaign.effectiveStatus=="ACTIVE"):
                    total_budget+=campaign.get_budget()
                    current_account_budget+=campaign.get_budget()

        total_spend_projected+=current_account_spend+(current_account_budget*days_left_this_month)
        print(f"{total_current_spend}+({total_budget}*{days_left_this_month})")
        #print(f'{total_current_spend}+({total_budget}*{days_left_this_month})')




        #for campaign in campaigns:
        #    #request adset data from adset API
        #    url=f'https://graph.facebook.com/v16.0/{account["id"]}/adsets?fields=daily_budget,effective_status,name,spend,campaign{{name,id,daily_budget}}&effective_status=["ACTIVE"]&date_preset=last_30d&access_token={access_token}'
        #    ret = requests.get(url)
        #    ret_adsets=json.loads(ret.text)
        #    print(ret_adsets)
        #    add_budget_to_adsets_from_ADSETS(ret_adsets['data'],adsets)

        print(f'total_current_spend: {total_current_spend}')
        print(f'total_budget: {total_budget}')
        print(f'total_spend_projected: {total_spend_projected}')
    return {
            'total_current_spend': total_current_spend,
            'total_budget': total_budget,
            'total_spend_projected': total_spend_projected
            }