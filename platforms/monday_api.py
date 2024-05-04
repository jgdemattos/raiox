import requests
import json

from dotenv import dotenv_values #pip

config=dotenv_values("./.env")
monday_token=config["monday_token"]


def request_client_data_on_monday(channel_id=0):
    apiKey = monday_token
    apiUrl = "https://api.monday.com/v2"
    headers = {"Authorization" : apiKey, "API-version" : '2024-01'}

    query="""query {
                boards (ids: 5611690845) {
                    name
                    state
                    id
                    items_page{
                        items{
                            group {
                                title
                          	}
                            name
                            id
                            column_values {
                                ... on MirrorValue {
                                    display_value
                                } 
                                id
                                value
                                text
                                column {
                                    id
                                    title
                                }
                            }
                        }
                    }
                }
            }"""
    request_data = {'query' : query}
    r = requests.post(url=apiUrl, json=request_data, headers=headers)
    data=json.loads(r.text)

    clients=[]

    for item in data['data']['boards'][0]['items_page']['items']:
        if(item['group']['title']=="Ativos"):
            clients.append(
                {
                    'cod':item['name'],
                    'monday_item_id':item['id'],
                    'meta_id':next(item for item in item['column_values'] if item['column']["title"] == "meta_id")['text'],
                    'meta_adaccount_ids':next(item for item in item['column_values'] if item['column']["title"] == "meta_adaccount_ids")['text'].split(",") if next(item for item in item['column_values'] if item['column']["title"] == "meta_adaccount_ids")['text'] != "" else [] ,
                    'google_id':next(item for item in item['column_values'] if item['column']["title"] == "google_id")['text'],
                    'channel_id':next(item for item in item['column_values'] if item['column']["title"] == "channel_id")['text'],
                    'health':next(item for item in item['column_values'] if item['column']["title"] == "health")['display_value'],
                    'satisfaction':next(item for item in item['column_values'] if item['column']["title"] == "satisfaction")['display_value'],
                    'engagement':next(item for item in item['column_values'] if item['column']["title"] == "engagement")['display_value'],
                    'gap':next(item for item in item['column_values'] if item['column']["title"] == "gap")['display_value'],
                        'min_revenue':next(item for item in item['column_values'] if item['column']["title"] == "min_revenue")['display_value'],
                        'ideal_revenue':next(item for item in item['column_values'] if item['column']["title"] == "ideal_revenue")['display_value'],
                        'min_investment':next(item for item in item['column_values'] if item['column']["title"] == "min_investment")['display_value'],
                        'real_investment':next(item for item in item['column_values'] if item['column']["title"] == "real_investment")['display_value'],
                        'real_revenue':next(item for item in item['column_values'] if item['column']["title"] == "real_revenue")['display_value'],
                    'name':item['name']
                })
        
    if(channel_id!=0):
        for item in clients:
            if(item['channel_id']==channel_id):
                return item

    return clients