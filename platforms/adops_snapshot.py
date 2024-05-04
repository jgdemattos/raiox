from flask import Flask, request, redirect
import requests
import math
import json
from datetime import date
from calendar import monthrange

from messagebuilder import MessageBuilder
from monday_api import request_client_data_on_monday
from meta_api import get_meta_adaccounts
from meta_api import get_meta_adsets
from meta_api import get_meta_campaigns
from meta_businessmanager import MetaBusinessmanager
from google_api import get_google_adaccounts

from dotenv import dotenv_values #pip

config=dotenv_values("./.env")
slack_token=config["SLACK_BOT_TOKEN"]


app = Flask(__name__)


import os
from supabase import create_client, Client

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

@app.route("/adops_snapshot/",methods = ['POST'])
def adops_snapshot():

    channel_id=0

    all_monday_data=request_client_data_on_monday()
    print(all_monday_data)
    for monday_data in all_monday_data:
        print(monday_data)

        message_builder=MessageBuilder(monday_data['name'], channel_id)

        if(monday_data['meta_id'] or monday_data['meta_adaccount_ids']):
            if(monday_data['meta_id']):

                meta_businessmanager_data=get_meta_adaccounts(monday_data['meta_id'])
                
                meta_adaccounts=meta_businessmanager_data['meta_adaccounts']

                meta_businessmanager=MetaBusinessmanager(meta_businessmanager_data['meta_businessmanager_name'],monday_data['meta_id'])


            else:
                LARANJEIRA_BM_ID=141239895510066

                meta_businessmanager_data=get_meta_adaccounts(LARANJEIRA_BM_ID)

                meta_adaccounts=meta_businessmanager_data['meta_adaccounts']

                meta_businessmanager=MetaBusinessmanager("LARANJEIRA",LARANJEIRA_BM_ID)

            meta_adaccounts_for_current_client=[]
            if(len(monday_data['meta_adaccount_ids'])==0):
                meta_adaccounts_for_current_client=meta_adaccounts
            else:
                for meta_adaccount in meta_adaccounts:
                    if(meta_adaccount.is_in_this_list(monday_data['meta_adaccount_ids'])):
                        meta_adaccounts_for_current_client.append(meta_adaccount)
                    
            meta_businessmanager.set_meta_adaccounts(meta_adaccounts_for_current_client)

            
            for meta_adaccount in meta_businessmanager.adaccounts:
                meta_adsets=get_meta_adsets(meta_adaccount)
                meta_campaigns=get_meta_campaigns(meta_adaccount, meta_adsets)
                meta_adaccount.set_campaigns(meta_campaigns)


            message_builder.set_businessmanagers([meta_businessmanager]) 

        if(monday_data['google_id']):
            google_adaccount=get_google_adaccounts(monday_data['google_id'])

            message_builder.set_google_accounts([google_adaccount])

        headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {slack_token}'
        }

        #res=requests.post(url="https://slack.com/api/chat.postMessage", json=message_builder.build_message(in_channel),
        #                                                            headers=headers
        #                                                            )

        #get_google_test(monday_data['google_id'])

        print(monday_data['name'])
        data, count = supabase.table('client_daily').insert({
                                                                'cod': monday_data['cod'], 
                                                                'budget': message_builder.calculate_total_projection()['account_budget']  or 0, 
                                                                'spend': message_builder.calculate_total_projection()['account_cost']  or 0, 
                                                                'projection': message_builder.calculate_total_projection()['total_spend_projected']  or 0, 
                                                                'health': monday_data['health'], 
                                                                'satisfaction': monday_data['satisfaction'], 
                                                                'engagement': monday_data['engagement'],
                                                                'gap': monday_data['gap'],
                                                                    'min_revenue': monday_data['min_revenue']  or 0,
                                                                    'ideal_revenue': monday_data['ideal_revenue']  or 0,
                                                                    'min_investment': monday_data['min_investment']  or 0,
                                                                    'real_investment': monday_data['real_investment'] or 0,
                                                                    'real_revenue': monday_data['real_revenue'] or 0,
                                                                'date':str(date.today())}
                                                            ).execute()

        #response = supabase.table('client_daily').select("*").execute()

        #print(response)
        #print(response.data)
    return "OK"




