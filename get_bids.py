# get_bids.py
import os
from dotenv import load_dotenv
import requests
import pandas as pd
import datetime
from xml.etree import ElementTree as ET

# 환경 변수에서 API 키를 로드
load_dotenv()
api_key = os.getenv('BID_API_KEY')

# 데이터 가져오기
def fetch_data(page_no, start_date, end_date):
    base_url = "http://apis.data.go.kr/1230000/BidPublicInfoService04/getBidPblancListInfoServc"
    params = {
        'serviceKey': api_key,
        'pageNo': page_no,
        'numOfRows': 999,
        'inqryBgnDt': start_date,
        'inqryEndDt': end_date
    }
    
    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        return response.content
    else:
        print(f"Failed to fetch data: {response.status_code}")
        print(f"Response content: {response.content}")
        return None

# XML 데이터 파싱
def parse_xml(data):
    root = ET.fromstring(data)
    body = root.find('.//body')
    if body is None:
        return []
    
    items = body.find('.//items')
    if items is None:
        return []
    
    item_list = []
    for item in items.findall('.//item'):
        item_data = {
            'bidNtceNo': item.find('bidNtceNo').text if item.find('bidNtceNo') is not None else '',
            'ntceInsttNm': item.find('ntceInsttNm').text if item.find('ntceInsttNm') is not None else '',
            'bidNtceNm': item.find('bidNtceNm').text if item.find('bidNtceNm') is not None else '',
            'presmptPrce': item.find('presmptPrce').text if item.find('presmptPrce') is not None else '',
            'bidNtceDt': item.find('bidNtceDt').text if item.find('bidNtceDt') is not None else ''
        }
        item_list.append(item_data)
        
    return item_list

# 데이터 CSV로 저장
def save_to_csv(data, file_path, columns):
    df = pd.DataFrame(data)
    df = df[columns]
    df.to_csv(file_path, index=False, encoding='utf-8-sig')
    print(f"Filtered data saved to {file_path}")

if __name__ == "__main__":
    start_date = (datetime.datetime.now() - datetime.timedelta(days=2)).strftime('%Y%m%d') + '0000'
    end_date = datetime.datetime.now().strftime('%Y%m%d') + '2359'
    
    all_data = []
    columns = ['bidNtceNo', 'ntceInsttNm', 'bidNtceNm', 'presmptPrce', 'bidNtceDt']
    file_path = "filtered_bids_data.csv"
    page_no = 1
    
    while True:
        data = fetch_data(page_no, start_date, end_date)
        if data:
            items = parse_xml(data)
            if not items:
                break
            all_data.extend(items)
            page_no += 1
        else:
            break
    
    if all_data:
        df_new = pd.DataFrame(all_data)
        
        if os.path.exists(file_path):
            df_existing = pd.read_csv(file_path)
            common_ids = df_existing['bidNtceNo'].isin(df_new['bidNtceNo']).sum()
            new_ids = len(df_new) - common_ids
            print(f"Total fetched IDs: {len(df_new)}")
            print(f"Existing IDs: {len(df_existing)}")
            print(f"Common IDs: {common_ids}")
            print(f"New unique IDs: {new_ids}")
            
            merged_df = pd.concat([df_existing, df_new]).drop_duplicates(subset='bidNtceNo', keep='last')
            merged_df.to_csv(file_path, index=False, encoding='utf-8-sig')
        else:
            save_to_csv(df_new, file_path, columns)
    else:
        print("No data found")

# python get_bids.py
