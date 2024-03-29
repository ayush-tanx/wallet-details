import os
import csv
import requests
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

COVALENT_API_KEY = os.environ['COVALENT_API_KEY']
include_zero_and_extra_records = False

datafile = "input.csv"
outputfile = "output/balances_{datetime_stamp}.csv"

api_url = 'https://api.covalenthq.com/v1/{chain_name}/address/{wallet_address}/balances_v2/?no-spam=true'
headers = {"Content-Type": "application/json"}
auth = (COVALENT_API_KEY, "")

networks = ['eth-mainnet', 'matic-mainnet', 'scroll-mainnet', 'optimism-mainnet', 'arbitrum-mainnet', 'linea-mainnet']

def get_wallet_details(chain_name, wallet_address):
    r = requests.get(url=api_url.format(chain_name=chain_name, wallet_address=wallet_address), headers=headers, auth=auth)
    if r.status_code == 200:
        return r.json()['data']
    else:
        print(r.json())
        return None

# read csv as a 2D array/list
data = list(csv.reader(open(datafile)))
data[0]+=['network', 'token', 'balance', 'value']   # headings

output_data = []
output_data.append(data[0])

for row in range(1, len(data)):
    record = data[row]
    wallet_address = record[1].strip()
    for network in networks:
        wallet_details = get_wallet_details(chain_name=network, wallet_address=wallet_address)
        if wallet_details:
            for item in wallet_details['items']:
                if (not item['pretty_quote'] or int(item['balance']) == 0 ) and not include_zero_and_extra_records:
                    continue
                new_record = record.copy()
                balance = int(item['balance'])/10**int(item['contract_decimals'])   # dequantizing
                new_record += [network, item['contract_ticker_symbol'], balance, f"${item['quote']}"]
                output_data.append(new_record)

# Write modified data to a new CSV file
with open(outputfile.format(datetime_stamp=str(datetime.now()).replace(' ', '_').replace(':', '.')), 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerows(output_data)