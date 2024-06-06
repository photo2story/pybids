import os
import subprocess
import json
import pandas as pd
import datetime

# Load API key from environment variables
from dotenv import load_dotenv
load_dotenv()
api_key = os.getenv('BID_API_KEY')

def fetch_data_with_curl(url, params):
    query_string = '&'.join([f"{key}={value}" for key, value in params.items()])
    url_with_params = f"{url}?{query_string}"
    
    try:
        result = subprocess.run(['curl', '-k', url_with_params], capture_output=True, text=True, encoding='utf-8')
        if result.returncode == 0:
            return result.stdout
        else:
            print("Failed to connect.")
    except Exception as e:
        print(f"An error occurred: {e}")
    return None

def update_data(file_path, url, params, columns, date_column):
    if os.path.exists(file_path):
        df_existing = pd.read_csv(file_path)
        last_update = pd.to_datetime(df_existing[date_column]).max()
        start_date = (last_update + pd.Timedelta(days=1)).strftime('%Y%m%d') + '0000'
    else:
        df_existing = pd.DataFrame(columns=columns)
        start_date = (datetime.datetime.now() - datetime.timedelta(days=30)).strftime('%Y%m%d') + '0000'

    end_date = datetime.datetime.now().strftime('%Y%m%d') + '2359'
    params['inqryBgnDt'] = start_date
    params['inqryEndDt'] = end_date

    all_data = []
    page_no = 1
    
    while True:
        params['pageNo'] = page_no
        data = fetch_data_with_curl(url, params)
        if data:
            json_data = json.loads(data)
            items = json_data.get('response', {}).get('body', {}).get('items', [])
            if not items:
                break
            all_data.extend(items)
            page_no += 1
        else:
            break
    
    if all_data:
        df_new = pd.DataFrame(all_data)
        df_new = df_new[columns]
        df_combined = pd.concat([df_existing, df_new]).drop_duplicates(subset=[columns[0]]).reset_index(drop=True)
        df_combined.to_csv(file_path, index=False, encoding='utf-8-sig')
        print(f"Data updated and saved to {file_path}")
    else:
        print("No new data found.")

def update_prebids_data():
    url = "https://apis.data.go.kr/1230000/HrcspSsstndrdInfoService/getPublicPrcureThngInfoServc"
    params = {
        'serviceKey': api_key,
        'numOfRows': 999,
        'type': 'json',
        'inqryDiv': '1'
    }
    columns = ['bfSpecRgstNo', 'orderInsttNm', 'prdctClsfcNoNm', 'asignBdgtAmt', 'rcptDt']
    update_data("filtered_prebids_data.csv", url, params, columns, 'rcptDt')

def update_bids_data():
    url = "https://apis.data.go.kr/1230000/HrcspSsstndrdInfoService/getPublicPrcureThngInfoServc"
    params = {
        'serviceKey': api_key,
        'numOfRows': 999,
        'type': 'json',
        'inqryDiv': '1'
    }
    columns = ['bidNtceNo', 'ntceInsttNm', 'bidNtceNm', 'presmptPrce', 'bidNtceDt']
    update_data("filtered_bids_data.csv", url, params, columns, 'bidNtceDt')
