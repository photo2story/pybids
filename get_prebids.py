# get_prebids.py

import os
from dotenv import load_dotenv
import subprocess
import json
import pandas as pd
import datetime
import sys

# 가상 환경 경로를 추가합니다.
venv_path = os.path.join(os.path.dirname(__file__), '.venv')
site_packages_path = os.path.join(venv_path, 'Lib', 'site-packages')

# 환경 변수에서 API 키를 로드
load_dotenv()
api_key = os.getenv('BID_API_KEY')

# cURL 명령어 실행
def fetch_data_with_curl(page_no, start_date, end_date):
    base_url = "http://apis.data.go.kr/1230000/HrcspSsstndrdInfoService/getPublicPrcureThngInfoServc"
    params = {
        'serviceKey': api_key,
        'pageNo': page_no,
        'numOfRows': 999,
        'inqryDiv': '1',
        'inqryBgnDt': start_date,
        'inqryEndDt': end_date,
        'type': 'json'
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

def save_to_csv(data, file_path, columns):
    df = pd.DataFrame(data)
    df = df[columns]
    df.to_csv(file_path, index=False, encoding='utf-8-sig')
    print(f"Filtered data saved to {file_path}")

if __name__ == "__main__":
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
                for item in items:
                    item['link'] = f"https://www.g2b.go.kr:8082/ep/preparation/prestd/preStdDtl.do?preStdRegNo={item['bfSpecRgstNo']}"
                all_data.extend(items)
                page_no += 1
            except json.JSONDecodeError as e:
                print(f"JSON decode error: {e}")
                print(f"Response content: {data}")
                break
        else:
            break
    
    if all_data:
        df_new = pd.DataFrame(all_data)
        columns = ['bfSpecRgstNo', 'orderInsttNm', 'prdctClsfcNoNm', 'asignBdgtAmt', 'rcptDt', 'link']
        if not os.path.exists('filtered_prebids_data.csv'):
            save_to_csv(df_new, 'filtered_prebids_data.csv', columns)
        else:
            df_existing = pd.read_csv('filtered_prebids_data.csv')
            common_ids = df_existing['bfSpecRgstNo'].isin(df_new['bfSpecRgstNo']).sum()
            new_ids = len(df_new) - common_ids
            print(f"Total fetched IDs: {len(df_new)}")
            print(f"Existing IDs: {len(df_existing)}")
            print(f"Common IDs: {common_ids}")
            print(f"New unique IDs: {new_ids}")
            
            merged_df = pd.concat([df_existing, df_new]).drop_duplicates(subset='bfSpecRgstNo', keep='last')
            merged_df.to_csv('filtered_prebids_data.csv', index=False, encoding='utf-8-sig')

        # 필터링된 데이터
        keywords = ["기본계획","설계", "타당성", "환경", "안전진단", "건설사업", "평가", "안전점검", "측량", "제안", "공모"]
        keyword_pattern = '|'.join(keywords)
        filtered_df = df_new[df_new['prdctClsfcNoNm'].str.contains(keyword_pattern, na=False)]
        if not filtered_df.empty:
            save_to_csv(filtered_df, 'filtered_prebids_data.csv', columns)
    else:
        print("No data found")


# python get_prebids.py