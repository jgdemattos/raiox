from flask import Flask, request, redirect #pip
from dotenv import dotenv_values #pip
import sys
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException

from google_account import GoogleAccount
from google_campaign import GoogleCampaign

def get_google_adaccounts(google_account_id):


    config=dotenv_values("./platforms/.env")
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
        ga_service = googleads_client.get_service("GoogleAdsService")

        query = """
            SELECT
                campaign.id,
                campaign.name,
                campaign.status,
                campaign_budget.amount_micros,
                metrics.cost_micros
            FROM campaign
            WHERE segments.date DURING THIS_MONTH
            ORDER BY campaign.id

        """
        # Issues a search request using streaming.
        stream = ga_service.search_stream(customer_id=google_account_id, query=query)


        for batch in stream:
            for google_campaign_data in batch.results:
                #print(
                #    f"Campaign with ID {google_campaign_data.campaign.id} and name "
                #    f'"{google_campaign_data.campaign.name}" was found.'
                #    f'"Budget: {google_campaign_data.campaign_budget.amount_micros}".'
                #    f'"Cost: {google_campaign_data.metrics.cost_micros}".'
                #    f'"*STATUS*: {google_campaign_data.campaign.status.name}".'
                #)
                google_campaign=GoogleCampaign(
                                                google_campaign_data.campaign.id, 
                                                google_campaign_data.campaign.name, 
                                                google_campaign_data.metrics.cost_micros, 
                                                google_campaign_data.campaign_budget.amount_micros, 
                                                google_campaign_data.campaign.status
                                                )
                google_campaigns.append(google_campaign)

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

    google_account.set_google_campaigns(google_campaigns)

    return google_account