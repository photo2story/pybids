# get_bidwin.py
import os
from dotenv import load_dotenv
import requests
import pandas as pd
import datetime

# 환경 변수에서 API 키를 로드
load_dotenv()
api_key = os.getenv('BID_API_KEY')

# 데이터 가져오기
def fetch_data(page_no, start_date, end_date):
    base_url = "https://apis.data.go.kr/1230000/ScsbidInfoService/getOpengResultListInfoServc"
    params = {
        'serviceKey': api_key,
        'pageNo': page_no,
        'numOfRows': 999,
        'type': 'json',
        'inqryDiv': 1,
        'inqryBgnDt': start_date,
        'inqryEndDt': end_date
    }
    
    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch data: {response.status_code}")
        return None

# 데이터 CSV로 저장
def save_to_csv(data, file_path, columns):
    df = pd.DataFrame(data)
    df = df[columns]
    df.to_csv(file_path, index=False, encoding='utf-8-sig')
    print(f"Filtered data saved to {file_path}")

if __name__ == "__main__":
    start_date = (datetime.datetime.now() - datetime.timedelta(days=3)).strftime('%Y%m%d') + '0000'
    end_date = datetime.datetime.now().strftime('%Y%m%d') + '2359'
    
    all_data = []
    page_no = 1
    target_company = "수성엔지니어링"
    
    while True:
        data = fetch_data(page_no, start_date, end_date)
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
        filtered_data = [item for item in all_data if target_company in item.get('opengCorpInfo', '')]
        if filtered_data:
            columns = ['bidNtceNo', 'ntceInsttNm', 'bidNtceNm', 'opengCorpInfo', 'sucsfbidAmt', 'opengDt']
            # 필요한 필드가 실제로 존재하는지 확인
            existing_columns = filtered_data[0].keys()
            columns = [col for col in columns if col in existing_columns]
            save_to_csv(filtered_data, 'filtered_bidwin_data.csv', columns)
        else:
            print(f"No matching data found for '{target_company}'")
    else:
        print("No data found")

# python get_bidwin.py