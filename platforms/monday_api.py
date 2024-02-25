import requests
import json
monday_token='eyJhbGciOiJIUzI1NiJ9.eyJ0aWQiOjI1MzUzMTM3NywiYWFpIjoxMSwidWlkIjozNzQwOTk4NSwiaWFkIjoiMjAyMy0wNC0yOFQxODowNDozOS4wMDBaIiwicGVyIjoibWU6d3JpdGUiLCJhY3RpZCI6MTA1NzAyNjUsInJnbiI6InVzZTEifQ.k5lf_2ccOP9fiETIKwaHUha3HDSagT0Qxx7rKk08MWY'

def request_client_data_on_monday(channel_id):
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
                            name
                            id
                            column_values {
                                id
                                column {
                                    id
                                    title
                                }
                                value
                                text
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
        clients.append(
            {
                'cod':item['name'],
                'monday_item_id':item['id'],
                'meta_id':next(item for item in item['column_values'] if item['column']["title"] == "meta_id")['text'],
                'meta_adaccount_ids':next(item for item in item['column_values'] if item['column']["title"] == "meta_adaccount_ids")['text'].split(",") if next(item for item in item['column_values'] if item['column']["title"] == "meta_adaccount_ids")['text'] != "" else [] ,
                'google_id':next(item for item in item['column_values'] if item['column']["title"] == "google_id")['text'],
                'channel_id':next(item for item in item['column_values'] if item['column']["title"] == "channel_id")['text'],
                'name':item['name']
             })
        
    for item in clients:
        if(item['channel_id']==channel_id):
            return item

    return None