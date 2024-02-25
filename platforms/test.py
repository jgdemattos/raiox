from flask import Flask, request, redirect #pip
from dotenv import dotenv_values #pip
import sys
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException

from google_account import GoogleAccount
from google_campaign import GoogleCampaign
#2608529109371599?fields=owned_ad_accounts{name,activities{object_name,actor_name,application_name,extra_data,date_time_in_timezone,event_time,object_type,translated_event_type}}
def get_google_test(google_account_id):


    config=dotenv_values("./.env")
    credentials={
                    "developer_token":config["developer_token"],
                    "refresh_token":config["refresh_token"],
                    "client_id":config["client_id"],
                    "client_secret":config["client_secret"],
                    "login_customer_id":config["mcc_id"],
                    "use_proto_plus":True,
                }

    googleads_client = GoogleAdsClient.load_from_dict(credentials,version="v14")

    google_account=GoogleAccount(google_account_id)

    google_campaigns=[]
    try:
        campaigns_data=main(googleads_client, google_account_id)
        for batch in campaigns_data:
            print(batch)

    except GoogleAdsException as ex:
        print(
            f'Request with ID "{ex.request_id}" failed with status '
            f'"{ex.error.code().name}" and includes the following errors:'
        )
        for error in ex.failure.errors:
            print(f'\tError with message "{error.message}".')
            if error.location:
                for field_path_element in error.location.field_path_elements:
                    print(f"\t\tOn field: {field_path_element.field_name}")




    return 'ok'


def main(client, customer_id):
    ga_service = client.get_service("GoogleAdsService")

    #query = """
    #    SELECT customer.status, customer.descriptive_name, billing_setup.status, billing_setup.payments_account FROM account_budget
    #"""

    query = """
        SELECT change_event.campaign, change_event.change_date_time, change_event.change_resource_type, change_event.user_email, campaign.name, campaign.id, change_event.old_resource, change_event.new_resource, change_event.resource_change_operation FROM change_event WHERE change_event.change_date_time DURING THIS_MONTH LIMIT 100
    """


    stream = ga_service.search_stream(customer_id=customer_id, query=query)

    return stream
