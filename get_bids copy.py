import os
from dotenv import load_dotenv
import requests
import pandas as pd
import datetime
from xml.etree import ElementTree as ET

# 환경 변수에서 API 키를 로드
load_dotenv()
api_key = os.getenv('BID_API_KEY')

# 키워드 리스트
keywords = ["기본", "설계", "계획", "조사", "타당성", "환경", "안전", "건설사업", "평가", "점검", "측량", "제안", "공모"]

# 데이터 가져오기
def fetch_data(page_no, start_date, end_date, keyword):
    base_url = "http://apis.data.go.kr/1230000/BidPublicInfoService04/getBidPblancListInfoServc01"
    params = {
        'serviceKey': api_key,
        'pageNo': page_no,
        'numOfRows': 999,
        'inqryDiv': 1,
        'inqryBgnDt': start_date,
        'inqryEndDt': end_date,
        'bidNtceNm': keyword
    }
    
    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        return response.content
    else:
        print(f"Failed to fetch data: {response.status_code}")
        print("Response content:", response.text)
        return None

# XML 데이터 파싱
def parse_xml(data):
    root = ET.fromstring(data)
    body = root.find('body')
    if body is None:
        return []
    
    items = body.find('items')
    if items is None:
        return []
    
    item_list = []
    for item in items.findall('item'):
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
    if 'sendOK' not in df.columns:
        df['sendOK'] = 0
    df = df[columns + ['sendOK']]
    df.to_csv(file_path, index=False, encoding='utf-8-sig')
    print(f"Data saved to {file_path}")

if __name__ == "__main__":
    start_date = (datetime.datetime.now() - datetime.timedelta(days=4)).strftime('%Y%m%d') + '0000'
    end_date = datetime.datetime.now().strftime('%Y%m%d') + '2359'
    
    all_data = []
    columns = ['bidNtceNo', 'ntceInsttNm', 'bidNtceNm', 'presmptPrce', 'bidNtceDt']
    file_path = "filtered_bids_data.csv"

    for keyword in keywords:
        page_no = 1
        while True:
            data = fetch_data(page_no, start_date, end_date, keyword)
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
        df_new['sendOK'] = 0  # 새로 추가된 항목의 sendOK는 0으로 설정
        df_new = df_new[columns + ['sendOK']]  # 필요한 열만 선택

        if os.path.exists(file_path):
            df_existing = pd.read_csv(file_path)
            if 'sendOK' not in df_existing.columns:
                df_existing['sendOK'] = 0
            df_existing = df_existing[columns + ['sendOK']]
            
            total_fetched_ids = len(df_new)
            existing_ids = len(df_existing)
            common_ids = df_existing['bidNtceNo'].isin(df_new['bidNtceNo']).sum()
            new_unique_ids = total_fetched_ids - common_ids
            
            print(f"Total fetched IDs: {total_fetched_ids}")
            print(f"Existing IDs: {existing_ids}")
            print(f"Common IDs: {common_ids}")
            print(f"New unique IDs: {new_unique_ids}")
            
            merged_df = pd.concat([df_existing, df_new]).drop_duplicates(subset='bidNtceNo', keep='last')
            merged_df.to_csv(file_path, index=False, encoding='utf-8-sig')
        else:
            save_to_csv(all_data, file_path, columns)

        # 필터링된 데이터 저장
        keyword_pattern = '|'.join(keywords)
        filtered_df = df_new[df_new['bidNtceNm'].str.contains(keyword_pattern, na=False)]
        save_to_csv(filtered_df, 'filtered_bids_data.csv', columns)
    else:
        print("No data found")

# python get_bids.py