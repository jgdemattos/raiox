from flask import Flask, request, redirect
import requests
import json

app = Flask(__name__)

eduzz_email="marcos@agencialaranjeira.com.br"
eduzz_public_key="80917706"
eduzz_api_key="766150357cfe88c"

@app.route("/gateways/",methods = ['GET'])
def raiox():
    url=f'https://api2.eduzz.com/credential/generate_token?email={eduzz_email}&publickey={eduzz_public_key}&apikey={eduzz_api_key}'
    ret = requests.post(url)
    token=json.loads(ret.text)['data']['token']

    url=f'https://api2.eduzz.com/sale/get_sale_list?start_date=2024-02-01&end_date=2024-02-20&page=1'
    res = requests.get(url,headers={'token':token})
    sales_response=json.loads(res.text)
    print(sales_response)

    return sales_response