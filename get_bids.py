# get_bids.py

import os
from dotenv import load_dotenv
import subprocess
import json
import pandas as pd
import datetime

# Load API key from environment variables
load_dotenv()
api_key = os.getenv('BID_API_KEY')

def fetch_data_with_curl(page_no, start_date, end_date):
    base_url = "https://apis.data.go.kr/1230000/HrcspSsstndrdInfoService/getPublicPrcureThngInfoServc"
    params = {
        'serviceKey': api_key,
        'pageNo': page_no,
        'numOfRows': 999,
        'type': 'json',
        'inqryDiv': '1',
        'inqryBgnDt': start_date,
        'inqryEndDt': end_date
    }
    query_string = '&'.join([f"{key}={value}" for key, value in params.items()])
    url = f"{base_url}?{query_string}"
    
    try:
        result = subprocess.run(['curl', '-k', url], capture_output=True, text=True, encoding='utf-8')
        if result.returncode == 0:
            return result.stdout
        else:
            print("Failed to connect.")
    except Exception as e:
        print(f"An error occurred: {e}")
    return None

if __name__ == "__main__":
    start_date = (datetime.datetime.now() - datetime.timedelta(days=30)).strftime('%Y%m%d') + '0000'
    end_date = datetime.datetime.now().strftime('%Y%m%d') + '2359'
    
    all_data = []
    page_no = 1
    
    while True:
        data = fetch_data_with_curl(page_no, start_date, end_date)
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
        df = pd.DataFrame(all_data)
        df = df[['bidNtceNo', 'ntceInsttNm', 'bidNtceNm', 'presmptPrce', 'bidNtceDt']]
        file_path = "bids_data.csv"
        df.to_csv(file_path, index=False, encoding='utf-8-sig')
        print(f"Filtered data saved to {file_path}")
        
        # Filter data based on keywords
        keywords = ["기본", "설계", "계획", "조사", "타당성", "환경", "안전", "건설사업", "평가", "점검", "측량", "제안", "공모"]
        keyword_pattern = '|'.join(keywords)
        filtered_df = df[df['bidNtceNm'].str.contains(keyword_pattern, na=False)]
        pd.set_option('display.max_rows', None)
        print(filtered_df)
        
        # Save filtered data
        filtered_file_path = "filtered_bids_data.csv"
        filtered_df.to_csv(filtered_file_path, index=False, encoding='utf-8-sig')
        print(f"Filtered data saved to {filtered_file_path}")
    else:
        print("No data found")



# python get_bids.py