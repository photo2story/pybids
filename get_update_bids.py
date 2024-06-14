# get_update_bids.py

import pandas as pd
import datetime
import os
import sys
# 가상 환경 경로를 추가합니다.
# venv_path = os.path.join(os.path.dirname(__file__), 'venv', 'Lib', 'site-packages')
# sys.path.append(venv_path)
def get_bid_updates(specific_date, new_only=False):
    df_bids = pd.read_csv("filtered_bids_data.csv")
    df_bids['bidNtceDt'] = pd.to_datetime(df_bids['bidNtceDt'], errors='coerce').dt.date
    
    if 'sendOK' not in df_bids.columns:
        df_bids['sendOK'] = 0
    
    if new_only:
        df_bids['sendOK'] = df_bids['sendOK'].fillna(0)
        updates = df_bids[(df_bids['bidNtceDt'] == specific_date) & (df_bids['sendOK'] == 0)]
    else:
        updates = df_bids[df_bids['bidNtceDt'] == specific_date]
    
    bid_updates = []
    for index, row in updates.iterrows():
        presmptPrce = f"{int(row['presmptPrce']):,}원" if pd.notnull(row['presmptPrce']) else "정보 없음"
        msg = (
            f"\n[{index + 1}] : 등록번호: {row['bidNtceNo']}\n"
            f"{row['ntceInsttNm']}\n"
            f"{row['bidNtceNm']}\n"
            f"{presmptPrce}\n"
            f"{row['bidNtceDt']}\n"
            f"http://www.g2b.go.kr:8081/ep/invitation/publish/bidInfoDtl.do?bidno={row['bidNtceNo']}"
        )
        bid_updates.append(msg)
        if new_only:
            df_bids.loc[df_bids['bidNtceNo'] == row['bidNtceNo'], 'sendOK'] = 1
    
    return bid_updates

def get_prebid_updates(specific_date, new_only=False):
    df_prebids = pd.read_csv("filtered_prebids_data.csv")
    df_prebids['rcptDt'] = pd.to_datetime(df_prebids['rcptDt'], errors='coerce').dt.date
    
    if 'sendOK' not in df_prebids.columns:
        df_prebids['sendOK'] = 0
    
    if new_only:
        df_prebids['sendOK'] = df_prebids['sendOK'].fillna(0)
        updates = df_prebids[(df_prebids['rcptDt'] == specific_date) & (df_prebids['sendOK'] == 0)]
    else:
        updates = df_prebids[df_prebids['rcptDt'] == specific_date]
    
    prebid_updates = []
    for index, row in updates.iterrows():
        asignBdgtAmt = f"{int(row['asignBdgtAmt']):,}원" if pd.notnull(row['asignBdgtAmt']) else "정보 없음"
        msg = (
            f"\n[{index + 1}] : 등록번호: {row['bfSpecRgstNo']}\n"
            f"{row['orderInsttNm']}\n"
            f"{row['prdctClsfcNoNm']}\n"
            f"{asignBdgtAmt}\n"
            f"{row['rcptDt']}\n"
            f"https://www.g2b.go.kr:8082/ep/preparation/prestd/preStdDtl.do?preStdRegNo={row['bfSpecRgstNo']}"
        )
        prebid_updates.append(msg)
        if new_only:
            df_prebids.loc[df_prebids['bfSpecRgstNo'] == row['bfSpecRgstNo'], 'sendOK'] = 1
    
    return prebid_updates

def get_bidwin_updates(specific_date, new_only=False):
    df_bidwin = pd.read_csv("filtered_bidwin_data.csv")
    df_bidwin['opengDt'] = pd.to_datetime(df_bidwin['opengDt'], errors='coerce').dt.date
    
    updates = df_bidwin[df_bidwin['opengDt'] == specific_date]
    
    bidwin_updates = []
    for index, row in updates.iterrows():
        msg = (
            f"\n[{index + 1}] : 입찰공고번호: {row['bidNtceNo']}\n"
            f"입찰공고명: {row['bidNtceNm']}\n"
            f"개찰일시: {row['opengDt']}\n"
            f"낙찰자: {row['opengCorpInfo']}\n"
        )
        bidwin_updates.append(msg)
    
    return bidwin_updates

def save_updated_dataframes():
    df_bids = pd.read_csv("filtered_bids_data.csv")
    df_prebids = pd.read_csv("filtered_prebids_data.csv")
    df_bidwin = pd.read_csv("filtered_bidwin_data.csv")
    
    if 'sendOK' not in df_bids.columns:
        df_bids['sendOK'] = 0
    
    if 'sendOK' not in df_prebids.columns:
        df_prebids['sendOK'] = 0
    
    df_bids.to_csv("filtered_bids_data.csv", index=False, encoding='utf-8-sig')
    df_prebids.to_csv("filtered_prebids_data.csv", index=False, encoding='utf-8-sig')
    df_bidwin.to_csv("filtered_bidwin_data.csv", index=False, encoding='utf-8-sig')

# python get_update_bids.py