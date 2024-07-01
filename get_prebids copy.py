import os
from dotenv import load_dotenv
import subprocess
import json
import pandas as pd
import datetime

# 환경 변수에서 API 키를 로드
load_dotenv()
api_key = os.getenv('BID_API_KEY')

# cURL 명령어 실행
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
            print(f"Response status code: {result.returncode}")
            print(f"Response content: {result.stdout[:500]}")  # 응답 내용 일부 출력
            return result.stdout
        else:
            print("Failed to connect.")
    except Exception as e:
        print(f"An error occurred: {e}")
    return None

# JSON 데이터를 CSV로 저장
def save_to_csv(data, file_path, columns):
    try:
        json_data = json.loads(data)
        items = json_data.get('response', {}).get('body', {}).get('items', [])
        if not items:
            print("No data found")
            return
        
        df = pd.DataFrame(items)
        df = df[columns]
        df.to_csv(file_path, index=False, encoding='utf-8-sig')
        print(f"Data saved to {file_path}")
    except Exception as e:
        print(f"An error occurred while saving to CSV: {e}")

if __name__ == "__main__":
    start_date = (datetime.datetime.now() - datetime.timedelta(days=2)).strftime('%Y%m%d') + '0000'
    end_date = datetime.datetime.now().strftime('%Y%m%d') + '2359'
    
    all_data = []
    page_no = 1
    columns = ['bfSpecRgstNo', 'orderInsttNm', 'prdctClsfcNoNm', 'asignBdgtAmt', 'rcptDt']
    file_path = "filtered_prebids_data.csv"

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
                print(f"Response content was not valid JSON:\n{data}")
                break
        else:
            break
    
    if all_data:
        df_new = pd.DataFrame(all_data)
        df_new = df_new[columns]  # 필요한 열만 선택
        
        if os.path.exists(file_path):
            df_existing = pd.read_csv(file_path)
            total_fetched_ids = len(df_new)
            existing_ids = len(df_existing)
            common_ids = df_existing['bfSpecRgstNo'].isin(df_new['bfSpecRgstNo']).sum()
            new_unique_ids = total_fetched_ids - common_ids
            
            print(f"Total fetched IDs: {total_fetched_ids}")
            print(f"Existing IDs: {existing_ids}")
            print(f"Common IDs: {common_ids}")
            print(f"New unique IDs: {new_unique_ids}")
            
            merged_df = pd.concat([df_existing, df_new]).drop_duplicates(subset='bfSpecRgstNo', keep='last')
            merged_df.to_csv(file_path, index=False, encoding='utf-8-sig')
        else:
            save_to_csv(data, file_path, columns)
    else:
        print("No data found")


# python get_prebids copy.py