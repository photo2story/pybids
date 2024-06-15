# get_bidwin.py

import os
from dotenv import load_dotenv
import subprocess
import pandas as pd
import datetime
import json
import sys
# 가상 환경 경로를 추가합니다.
# venv_path = os.path.join(os.path.dirname(__file__), 'venv', 'Lib', 'site-packages')
# sys.path.append(venv_path)
# 환경 변수에서 API 키를 로드
load_dotenv()
api_key = os.getenv('BID_API_KEY')

# cURL 명령어 실행
def fetch_data_with_curl(page_no, start_date, end_date):
    base_url = "https://apis.data.go.kr/1230000/ScsbidInfoService/getOpengResultListInfoServc"
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
            return json.loads(result.stdout)
        else:
            print("Failed to connect.")
    except Exception as e:
        print(f"An error occurred: {e}")
    return None

# 데이터 CSV로 저장
def save_to_csv(data, file_path, columns):
    df = pd.DataFrame(data)
    df = df[columns]
    df.to_csv(file_path, index=False, encoding='utf-8-sig')
    print(f"Filtered data saved to {file_path}")

if __name__ == "__main__":
    start_date = (datetime.datetime.now() - datetime.timedelta(days=6)).strftime('%Y%m%d') + '0000'
    end_date = datetime.datetime.now().strftime('%Y%m%d') + '2359'
    
    all_data = []
    page_no = 1
    target_companies = ["수성엔지니어링", "도화", "건화", "한국종합", "동명", "유신",
                        "이산", "케이지", "삼안", "동해", "다산", "제일", "삼보"
                        ]  # 여러 개의 회사를 포함하는 리스트
    keywords = ["설계", "계획", "타당성", "환경", "안전", "건설사업", "평가", "점검", "측량"]  # 필터링할 키워드 리스트
    
    while True:
        data = fetch_data_with_curl(page_no, start_date, end_date)
        if data:
            try:
                items = data.get('response', {}).get('body', {}).get('items', [])
                if not items:
                    print(f"No items found on page {page_no}")
                    break
                all_data.extend(items)
                print(f"Data fetched successfully for page {page_no}")
                page_no += 1
            except Exception as e:
                print(f"An error occurred: {e}")
                print(f"Response content: {data}")
                break
        else:
            break
    
    if all_data:
        filtered_data = [
            item for item in all_data 
            if any(company in item.get('opengCorpInfo', '') for company in target_companies) 
            and any(keyword in item.get('bidNtceNm', '') for keyword in keywords)
        ]
        if filtered_data:
            columns = ['bidNtceNo', 'ntceInsttNm', 'bidNtceNm', 'opengCorpInfo', 'sucsfbidAmt', 'opengDt']
            # 필요한 필드가 실제로 존재하는지 확인
            existing_columns = filtered_data[0].keys()
            columns = [col for col in columns if col in existing_columns]
            save_to_csv(filtered_data, 'filtered_bidwin_data.csv', columns)
        else:
            print(f"No matching data found for companies: {', '.join(target_companies)} with keywords: {', '.join(keywords)}")
    else:
        print("No data found")

# python get_bidwin.py