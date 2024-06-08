import os
from dotenv import load_dotenv
import subprocess
import json
import pandas as pd
import datetime

# 환경 변수에서 API 키를 로드
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

def update_prebids_data():
    start_date = (datetime.datetime.now() - datetime.timedelta(days=2)).strftime('%Y%m%d') + '0000'
    end_date = datetime.datetime.now().strftime('%Y%m%d') + '2359'
    
    all_data = []
    page_no = 1
    
    while True:
        data = fetch_data_with_curl(page_no, start_date, end_date)
        if data:
            try:
                json_data = json.loads(data)
                items = json_data.get('response', {}).get('body', {}).get('items', [])
                if not items:
                    break
                all_data.extend(items)
                page_no += 1
            except json.JSONDecodeError as e:
                print(f"JSON decode error: {e}")
                print(f"Response content was not valid JSON:\n{data[:1000]}")  # Displaying the first 1000 characters for context
                break
        else:
            break
    
    if all_data:
        columns = ['bfSpecRgstNo', 'orderInsttNm', 'prdctClsfcNoNm', 'asignBdgtAmt', 'rcptDt']
        df_new = pd.DataFrame(all_data)[columns]
        
        file_path = "filtered_prebids_data.csv"
        if os.path.exists(file_path):
            df_existing = pd.read_csv(file_path)
            common_ids = df_existing['bfSpecRgstNo'].isin(df_new['bfSpecRgstNo']).sum()
            unique_new = len(df_new) - common_ids
            total_ids = len(df_existing) + unique_new
            print(f"Total fetched IDs: {len(df_new)}")
            print(f"Existing IDs: {len(df_existing)}")
            print(f"Common IDs: {common_ids}")
            print(f"New unique IDs: {unique_new}")
            
            merged_df = pd.concat([df_existing, df_new]).drop_duplicates(subset='bfSpecRgstNo', keep='last')
            merged_df.to_csv(file_path, index=False, encoding='utf-8-sig')
        else:
            df_new.to_csv(file_path, index=False, encoding='utf-8-sig')
    else:
        print("No data found")

if __name__ == "__main__":
    update_prebids_data()




# python get_prebids.py