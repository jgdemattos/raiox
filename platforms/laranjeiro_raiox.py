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
from test import get_google_test


from dotenv import dotenv_values #pip

config=dotenv_values("./.env")
slack_token=config["SLACK_BOT_TOKEN"]


app = Flask(__name__)

@app.route("/raiox/",methods = ['POST'])
def raiox():
    if request.form and 'channel_id' in request.form:
        channel_id = request.form['channel_id']
        in_channel = request.form['in_channel']
        response_url = request.form['response_url']
    else:
        return 'ERROR: no channel_id'

    #receipt = requests.post(response_url,json={'text': 'Buscando dados...'})

    monday_data=request_client_data_on_monday(channel_id)

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

    res=requests.post(url="https://slack.com/api/chat.postMessage", json=message_builder.build_message(in_channel),
                                                                headers=headers
                                                                )


    #get_google_test(monday_data['google_id'])

    return 'ok'

