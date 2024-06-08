import pandas as pd
import json

def csv_to_json(bids_csv_file, prebids_csv_file, json_file_path):
    # CSV 파일 읽기
    bids_df = pd.read_csv(bids_csv_file)
    prebids_df = pd.read_csv(prebids_csv_file)
    
    # 필요한 데이터 추출
    bids = bids_df[['bidNtceDt', 'bidNtceNm']].to_dict(orient='records')
    prebids = prebids_df[['rcptDt', 'prdctClsfcNoNm']].to_dict(orient='records')

    # JSON 데이터 구성
    data = {
        'bids': bids,
        'prebids': prebids
    }

    # JSON 파일로 저장
    with open(json_file_path, 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)

# 파일 경로 설정
bids_csv_file = 'filtered_bids_data.csv'  # 공고 CSV 파일 경로
prebids_csv_file = 'filtered_prebids_data.csv'  # 사전공고 CSV 파일 경로
json_file_path = 'data.json'  # 출력 JSON 파일 경로

# CSV에서 JSON으로 변환
csv_to_json(bids_csv_file, prebids_csv_file, json_file_path)


# python export_json.py
