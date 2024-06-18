import pandas as pd
import git
import os
import sys

# 가상 환경 경로를 추가합니다.
venv_path = os.path.join(os.path.dirname(__file__), 'venv', 'Lib', 'site-packages')
sys.path.append(venv_path)

# 로컬 저장소 경로와 CSV 파일 경로를 설정합니다.
REPO_PATH = '/path/to/your/local/repo'  # 여기에 실제 로컬 저장소 경로를 입력하세요.
BIDS_FILE_PATH = os.path.join(REPO_PATH, 'filtered_bids_data.csv')
PREBIDS_FILE_PATH = os.path.join(REPO_PATH, 'filtered_prebids_data.csv')
BIDWIN_FILE_PATH = os.path.join(REPO_PATH, 'filtered_bidwin_data.csv')

# GitHub 토큰을 환경 변수에서 가져옵니다.
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
GITHUB_REPO_URL = f'https://{GITHUB_TOKEN}@github.com/photo2story/pybids.git'

load_dotenv()

def update_sendOK(file_path, bid_no):
    df = pd.read_csv(file_path)
    if 'sendOK' not in df.columns:
        df['sendOK'] = 0
    df.loc[df['bidNtceNo'] == bid_no, 'sendOK'] = 4
    df.to_csv(file_path, index=False, encoding='utf-8-sig')

# update_sendOK('filtered_bids_data.csv', 'your_bid_number')
# update_sendOK('filtered_prebids_data.csv', 'your_bid_number')

def git_commit_and_push(repo_path, file_path, message):
    repo = git.Repo(repo_path)
    repo.git.add(file_path)
    repo.index.commit(message)
    origin = repo.remote(name='origin')
    origin.set_url(GITHUB_REPO_URL)  # 원격 저장소 URL을 토큰을 포함하여 설정합니다.
    origin.push()
    print(f"Committed and pushed changes to {repo_path}")

if __name__ == "__main__":
    bidNtceNo = sys.argv[1]  # 커맨드라인에서 인자를 받아옵니다.
    filePath = sys.argv[2]
    update_sendOK(bidNtceNo, filePath)
    git_commit_and_push(REPO_PATH, filePath, f"Update sendOK to 4 for bid number {bidNtceNo}")

# python update_sendOK.py