# update_sendOK.py

import pandas as pd
import git
import os
import sys
import requests
from dotenv import load_dotenv  # dotenv 모듈 import

# 가상 환경 경로를 추가합니다.
venv_path = os.path.join(os.path.dirname(__file__), '.venv', 'Lib', 'site-packages')
sys.path.append(venv_path)

# 환경 변수 로드
load_dotenv()

# 프로젝트 루트 디렉토리에 있는 파일 경로 설정
REPO_PATH = os.path.dirname(os.path.abspath(__file__))  # 현재 스크립트의 디렉토리를 사용
BIDS_FILE_PATH = os.path.join(REPO_PATH, 'filtered_bids_data.csv')
PREBIDS_FILE_PATH = os.path.join(REPO_PATH, 'filtered_prebids_data.csv')
BIDWIN_FILE_PATH = os.path.join(REPO_PATH, 'filtered_bidwin_data.csv')

# GitHub 토큰을 환경 변수에서 가져옵니다.
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
DISCORD_WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK_URL')
GITHUB_REPO_URL = f'https://{GITHUB_TOKEN}@github.com/photo2story/pybids.git'

def update_sendOK(file_path, bid_no):
    df = pd.read_csv(file_path)
    if 'sendOK' not in df.columns:
        df['sendOK'] = 0
    df.loc[df['bidNtceNo'] == bid_no, 'sendOK'] = 4
    df.to_csv(file_path, index=False, encoding='utf-8-sig')

def git_commit_and_push(repo_path, file_path, message):
    repo = git.Repo(repo_path)
    repo.git.add(file_path)
    repo.index.commit(message)
    origin = repo.remote(name='origin')
    origin.set_url(GITHUB_REPO_URL)  # 원격 저장소 URL을 토큰을 포함하여 설정합니다.
    origin.push()
    print(f"Committed and pushed changes to {repo_path}")

def send_discord_message(bid_no):
    message = f"등록번호 {bid_no} 이(가) 체크되었습니다."
    response = requests.post(DISCORD_WEBHOOK_URL, json={"content": message})
    if response.status_code != 204:
        print(f"Failed to send Discord message: {response.status_code}, {response.text}")

if __name__ == "__main__":
    filePath = sys.argv[1]  # 커맨드라인에서 인자를 받아옵니다.
    bidNtceNo = sys.argv[2]
    update_sendOK(filePath, bidNtceNo)
    git_commit_and_push(REPO_PATH, filePath, f"Update sendOK to 4 for bid number {bidNtceNo}")
    send_discord_message(bidNtceNo)


# python update_sendOK.py filtered_bids_data.csv 000000000
