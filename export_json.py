import pandas as pd
import json

def csv_to_json(bids_csv_file, prebids_csv_file, json_file_path):
    # CSV 파일을 읽어 DataFrame으로 변환
    bids_df = pd.read_csv(bids_csv_file)
    prebids_df = pd.read_csv(prebids_csv_file)

    # 날짜와 품명이 있는 데이터만 필터링
    bids_df = bids_df.dropna(subset=['bidNtceDt', 'bidNtceNm'])
    prebids_df = prebids_df.dropna(subset=['rcptDt', 'prdctClsfcNoNm'])

    # bidNtceDt와 rcptDt가 NaN인 경우를 필터링
    bids_df = bids_df[bids_df['bidNtceDt'].apply(lambda x: x == x)]  # NaN인 경우 False로 변환
    prebids_df = prebids_df[prebids_df['rcptDt'].apply(lambda x: x == x)]  # NaN인 경우 False로 변환

    # 필요한 열만 선택
    bids_df = bids_df[['bidNtceDt', 'bidNtceNm']]
    prebids_df = prebids_df[['rcptDt', 'prdctClsfcNoNm']]

    # DataFrame을 딕셔너리로 변환
    bids_data = bids_df.to_dict(orient='records')
    prebids_data = prebids_df.to_dict(orient='records')

    # JSON 형식으로 저장
    data = {
        'bids': bids_data,
        'prebids': prebids_data
    }

    with open(json_file_path, 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)

# 파일 경로 설정
bids_csv_file = 'filtered_bids_data.csv'
prebids_csv_file = 'filtered_prebids_data.csv'
json_file_path = 'data.json'

# 변환 함수 호출
csv_to_json(bids_csv_file, prebids_csv_file, json_file_path)


# python export_json.py
