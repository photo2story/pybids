import pandas as pd

# 기존 CSV 파일 로드
file_path = "filtered_bids_data.csv"
df_existing = pd.read_csv(file_path)

# 중복된 열 제거
if 'presmptPrce' in df_existing.columns:
    df_existing = df_existing.loc[:, ~df_existing.columns.duplicated()]

# CSV 파일 저장
df_existing.to_csv(file_path, index=False, encoding='utf-8-sig')

print(f"File {file_path} has been cleaned up.")


# python arrage_csv.py
