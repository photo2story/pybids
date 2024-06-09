# get_prebids.py
# get_prebids.py
import os
from dotenv import load_dotenv
import subprocess
import json
import pandas as pd
import datetime

# 환경 변수에서 API 키를 로드
load_dotenv()
api_key = os.getenv('BID_API_KEY')

# 키워드 리스트# get_prebids.py
import os
from dotenv import load_dotenv
import subprocess
import pandas as pd
import datetime
import xml.etree.ElementTree as ET

# 환경 변수에서 API 키를 로드
load_dotenv()
api_key = os.getenv('PREBID_API_KEY')

# 키워드 리스트
keywords = ["기본", "설계", "계획", "조사", "타당성", "환경", "안전", "건설사업", "평가", "점검", "측량", "제안", "공모"]

# cURL 명령어 실행
def fetch_data_with_curl(page_no, start_date, end_date, keyword):
    base_url = "http://apis.data.go.kr/1230000/HrcspSsstndrdInfoService/getThngDetailMetaInfoServc"
    params = {
        'serviceKey': api_key,
        'pageNo': page_no,
        'numOfRows': 999,
        'inqryBgnDt': start_date,
        'inqryEndDt': end_date,
        'prdctClsfcNoNm': keyword  # API가 키워드 필터링을 지원
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

def parse_xml(xml_data):
    root = ET.fromstring(xml_data)
    items = root.find('body').find('items')
    data = []
    for item in items.findall('item'):
        data.append({
            'bfSpecRgstNo': item.find('bfSpecRgstNo').text,
            'orderInsttNm': item.find('orderInsttNm').text,
            'prdctClsfcNoNm': item.find('prdctClsfcNoNm').text,
            'asignBdgtAmt': item.find('asignBdgtAmt').text,
            'rcptDt': item.find('rcptDt').text
        })
    return data

def save_to_csv(data, file_path, columns):
    df = pd.DataFrame(data)
    df = df[columns]
    df.to_csv(file_path, index=False, encoding='utf-8-sig')
    print(f"Filtered data saved to {file_path}")

if __name__ == "__main__":
    start_date = (datetime.datetime.now() - datetime.timedelta(days=30)).strftime('%Y%m%d') + '0000'
    end_date = datetime.datetime.now().strftime('%Y%m%d') + '2359'
    
    all_data = []
    for keyword in keywords:
        page_no = 1
        while True:
            data = fetch_data_with_curl(page_no, start_date, end_date, keyword)
            if data:
                try:
                    parsed_data = parse_xml(data)
                    if not parsed_data:
                        break
                    all_data.extend(parsed_data)
                    page_no += 1
                except ET.ParseError as e:
                    print(f"XML parse error: {e}")
                    print(f"Response content: {data}")
                    break
            else:
                break
    
    if all_data:
        columns = ['bfSpecRgstNo', 'orderInsttNm', 'prdctClsfcNoNm', 'asignBdgtAmt', 'rcptDt']
        save_to_csv(all_data, 'filtered_prebids_data.csv', columns)
    else:
        print("No data found")

keywords = ["기본", "설계", "계획", "조사", "타당성", "환경", "안전", "건설사업", "평가", "점검", "측량", "제안", "공모"]

# cURL 명령어 실행
def fetch_data_with_curl(page_no, start_date, end_date, keyword):
    base_url = "http://apis.data.go.kr/1230000/HrcspSsstndrdInfoService/getThngDetailMetaInfoServc"
    params = {
        'serviceKey': api_key,
        'pageNo': page_no,
        'numOfRows': 999,
        'type': 'json',
        'inqryBgnDt': start_date,
        'inqryEndDt': end_date,
        'prdctClsfcNoNm': keyword  # API가 키워드 필터링을 지원
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
    start_date = (datetime.datetime.now() - datetime.timedelta(days=30)).strftime('%Y%m%d') + '0000'
    end_date = datetime.datetime.now().strftime('%Y%m%d') + '2359'
    
    all_data = []
    for keyword in keywords:
        page_no = 1
        while True:
            data = fetch_data_with_curl(page_no, start_date, end_date, keyword)
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
                    print(f"Response content: {data}")
                    break
            else:
                break
    
    if all_data:
        df_new = pd.DataFrame(all_data)
        columns = ['bfSpecRgstNo', 'orderInsttNm', 'prdctClsfcNoNm', 'asignBdgtAmt', 'rcptDt']

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
    else:
        print("No data found")



# python get_prebids.py