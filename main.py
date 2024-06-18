# main.py

from flask import Flask
from threading import Thread
import asyncio
import os
import pandas as pd
from dotenv import load_dotenv
import discord
from discord.ext import commands, tasks
import datetime
import subprocess
from get_update_bids import get_bid_updates, get_prebid_updates, get_bidwin_updates, save_updated_dataframes
import tracemalloc
# 가상 환경 활성화 경로
venv_path = os.path.join(os.path.dirname(__file__), '.venv')
site_packages_path = os.path.join(venv_path, 'Lib', 'site-packages')

# 환경 변수에서 API 키를 로드
load_dotenv()

app = Flask('')

@app.route('/')
def home():
    return "I'm alive"

def run():
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 8080)))

def keep_alive():
    server = Thread(target=run)
    server.start()

keep_alive()# main.py에 추가
# tracemalloc.start()# Discord 설정

# Discord 설정
TOKEN = os.getenv('DISCORD_APPLICATION_TOKEN')
CHANNEL_ID = os.getenv('DISCORD_CHANNEL_ID')

intents = discord.Intents.default()
intents.messages = True
client = discord.Client(intents=intents)

bot = commands.Bot(command_prefix='', intents=intents)

# 시작하기 전에 데이터를 업데이트
@bot.event
async def on_ready():
    print(f'Bot이 성공적으로 로그인했습니다: {bot.user.name}')
    channel = bot.get_channel(int(CHANNEL_ID))
    if channel:
        await channel.send(f'Bot이 성공적으로 로그인했습니다: {bot.user.name}')
        await channel.send("사용 가능한 명령어:\n- `bid <검색어>`: 공고 검색\n- `prebid <검색어>`: 사전 공고 검색\n- `bid win`: 오늘의 낙찰자\n- `show new`: 새로운 공고 알림\n- `show <YYYYMMDD>`: 특정 날짜의 새로운 공고 검색")
    
    if not update_data_task.is_running():
        update_data_task.start()


@bot.command(name='ping')
async def ping(ctx):
    await ctx.send('pong')

@bot.command(name='prebid')
async def prebid(ctx, *, query: str):
    if query.startswith('n '):
        prebid_number = query.split(' ')[1]
        url = f"https://www.g2b.go.kr:8082/ep/preparation/prestd/preStdDtl.do?preStdRegNo={prebid_number}"
        await ctx.send(url)
    else:
        num, keywords = query.split(' ', 1)
        num = int(num)
        keywords_list = keywords.split(',')
        df = pd.read_csv("filtered_prebids_data.csv")
        filtered_df = df[df['prdctClsfcNoNm'].str.contains('|'.join(keywords_list), na=False)]
        filtered_df = filtered_df.head(num)

        if filtered_df.empty:
            await ctx.send(f"No results found for '{keywords}'")
        else:
            messages = []
            for index, row in filtered_df.iterrows():
                asignBdgtAmt = f"{int(row['asignBdgtAmt']):,}원" if pd.notnull(row['asignBdgtAmt']) else "정보 없음"
                msg = (
                    f"\n[{index + 1}]\n"
                    f"\n등록번호: {row['bfSpecRgstNo']}\n"
                    f"{row['orderInsttNm']}\n"
                    f"{row['prdctClsfcNoNm']}\n"
                    f"{asignBdgtAmt}\n"
                    f"{row['rcptDt']}\n"
                    f"링크: http://www.g2b.go.kr:8081/ep/invitation/publish/bidInfoDtl.do?bidno={row['bidNtceNo']}\n"
                )
                messages.append(msg)

            for message in messages:
                await ctx.send(message)

@bot.command(name='bid')
async def bid(ctx, *, query: str):
    if query.startswith('n '):
        bid_number = query.split(' ')[1]
        url = f"http://www.g2b.go.kr:8081/ep/invitation/publish/bidInfoDtl.do?bidno={bid_number}"
        await ctx.send(url)
    else:
        num, keywords = query.split(' ', 1)
        num = int(num)
        keywords_list = keywords.split(',')
        df = pd.read_csv("filtered_bids_data.csv")
        filtered_df = df[df['bidNtceNm'].str.contains('|'.join(keywords_list), na=False)]
        filtered_df = filtered_df.head(num)

        if filtered_df.empty:
            await ctx.send(f"No results found for '{keywords}'")
        else:
            messages = []
            for index, row in filtered_df.iterrows():
                try:
                    presmptPrce = f"{int(row['presmptPrce']):,}원" if pd.notnull(row['presmptPrce']) else "정보 없음"
                except KeyError:
                    presmptPrce = "정보 없음"
                msg = (
                    f"\n[{index + 1}]\n"
                    f"\n등록번호: {row['bidNtceNo']}\n"
                    f"{row['ntceInsttNm']}\n"
                    f"{row['bidNtceNm']}\n"
                    f"{presmptPrce}\n"
                    f"{row['bidNtceDt']}\n"
                    f"http://www.g2b.go.kr:8081/ep/invitation/publish/bidInfoDtl.do?bidno={row['bidNtceNo']}"
                )
                messages.append(msg)

            for message in messages:
                await ctx.send(message)

@bot.command(name='bid win')
async def bid_win(ctx):
    df = pd.read_csv("filtered_bidwin_data.csv")
    today_date = datetime.datetime.now().strftime('%Y-%m-%d')
    filtered_df = df[df['opengDt'].str.startswith(today_date)]
    filtered_df = filtered_df[filtered_df['opengCorpInfo'].str.contains('수성엔지니어링')]

    if filtered_df.empty:
        await ctx.send("오늘의 낙찰자 정보가 없습니다.")
    else:
        messages = []
        for index, row in filtered_df.iterrows():
            try:
                sucsfbidAmt = f"{int(row['sucsfbidAmt']):,}원" if pd.notnull(row['sucsfbidAmt']) else "정보 없음"
            except KeyError:
                sucsfbidAmt = "정보 없음"
            msg = (
                f"\n[{index + 1}]\n"
                f"\n입찰공고번호: {row['bidNtceNo']}\n"
                f"입찰공고명: {row['bidNtceNm']}\n"
                f"낙찰금액: {sucsfbidAmt}\n"
                f"개찰일시: {row['opengDt']}\n"
                f"낙찰자: {row['opengCorpInfo']}\n"
                f"링크: http://www.g2b.go.kr:8081/ep/invitation/publish/bidInfoDtl.do?bidno={row['bidNtceNo']}\n"
            )
            messages.append(msg)

        for message in messages:
            await ctx.send(message)

@bot.command(name='show')
async def show(ctx, *, query: str):
    if query.lower() == "new":
        await show_updates(ctx.channel, datetime.date.today())
    else:
        specific_date = datetime.datetime.strptime(query, "%Y%m%d").date()
        await show_date(ctx.channel, specific_date)

async def show_date(channel, specific_date):
    bid_updates = get_bid_updates(specific_date)
    prebid_updates = get_prebid_updates(specific_date)
    bidwin_updates = get_bidwin_updates(specific_date)

    if bid_updates:
        await channel.send("**해당 날짜의 입찰 공고:**")
        for message in bid_updates:
            await channel.send(message)
    else:
        await channel.send("해당 날짜의 새로운 입찰 공고가 없습니다.")

    if prebid_updates:
        await channel.send("**해당 날짜의 사전 공고:**")
        for message in prebid_updates:
            await channel.send(message)
    else:
        await channel.send("해당 날짜의 새로운 사전 공고가 없습니다.")
    
    if bidwin_updates:
        await channel.send("**해당 날짜의 낙찰 정보:**")
        for message in bidwin_updates:
            await channel.send(message)
    else:
        await channel.send("해당 날짜의 새로운 낙찰 정보가 없습니다.")

async def show_updates(channel, specific_date):
    bid_updates = get_bid_updates(specific_date, new_only=True)
    prebid_updates = get_prebid_updates(specific_date, new_only=True)
    bidwin_updates = get_bidwin_updates(specific_date, new_only=True)

    if bid_updates:
        await channel.send("**오늘의 입찰 공고:**")
        for message in bid_updates:
            await channel.send(message)
    else:
        await channel.send("오늘의 새로운 입찰 공고가 없습니다.")

    if prebid_updates:
        await channel.send("**오늘의 사전 공고:**")
        for message in prebid_updates:
            await channel.send(message)
    else:
        await channel.send("오늘의 새로운 사전 공고가 없습니다.")
    
    if bidwin_updates:
        await channel.send("**오늘의 낙찰 정보:**")
        for message in bidwin_updates:
            await channel.send(message)
    else:
        await channel.send("오늘의 새로운 낙찰 정보가 없습니다.")
    
    save_updated_dataframes()
    
import concurrent.futures

# Define the update task
@tasks.loop(hours=24)  # Update data every 24 hours
async def update_data_task():
    scripts = ["get_prebids.py", "get_bids.py", "get_bidwin.py"]

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(fetch_data_and_update, script) for script in scripts]
        for future in concurrent.futures.as_completed(futures):
            try:
                future.result()
            except Exception as e:
                print(f"An error occurred: {e}")

    # Ensure that the export_json.py script runs after other scripts have completed
    fetch_data_and_update("export_json.py")

    channel = bot.get_channel(int(CHANNEL_ID))
    if channel:
        today = datetime.date.today()
        yesterday = today - datetime.timedelta(days=1)
        await show_updates(channel, today)
        await show_updates(channel, yesterday)




# Function to run a script within the virtual environment
def fetch_data_and_update(script_name):
    venv_activate = os.path.join('D:\\OneDrive\\Work\\Source\\Repos\\pybids\\.venv\\Scripts\\Activate.ps1')
    command = f'powershell -Command "{venv_activate}; python {script_name}"'
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Script {script_name} failed with status code {result.returncode}.")
        print(f"Error message: {result.stderr}")
    else:
        print(f"Script {script_name} finished successfully.")


async def send_daily_updates():
    channel = bot.get_channel(int(CHANNEL_ID))
    today = datetime.date.today()  # 오늘의 날짜로 설정
    
    # 필터링된 공고
    bid_updates = []
    prebid_updates = []

    # Bid updates
    df_bids = pd.read_csv("filtered_bids_data.csv")
    df_bids['bidNtceDt'] = pd.to_datetime(df_bids['bidNtceDt']).dt.date
    new_bids = df_bids[df_bids['bidNtceDt'] == today]
    for index, row in new_bids.iterrows():
        msg = (
            f"\n[{index + 1}] : 등록번호: {row['bidNtceNo']}\n"
            f"{row['ntceInsttNm']}\n"
            f"{row['bidNtceNm']}\n"
            f"{row['presmptPrce']}원\n"
            f"{row['bidNtceDt']}\n"
            f"http://www.g2b.go.kr:8081/ep/invitation/publish/bidInfoDtl.do?bidno={row['bidNtceNo']}"
        )
        bid_updates.append(msg)

    # Prebid updates
    df_prebids = pd.read_csv("filtered_prebids_data.csv")
    df_prebids['rcptDt'] = pd.to_datetime(df_prebids['rcptDt']).dt.date
    new_prebids = df_prebids[df_prebids['rcptDt'] == today]
    for index, row in new_prebids.iterrows():
        asignBdgtAmt = f"{int(row['asignBdgtAmt']):,}원"
        msg = (
            f"\n[{index + 1}] : 등록번호: {row['bfSpecRgstNo']}\n"
            f"{row['orderInsttNm']}\n"
            f"{row['prdctClsfcNoNm']}\n"
            f"{asignBdgtAmt}\n"
            f"{row['rcptDt']}\n"
            f"https://www.g2b.go.kr:8082/ep/preparation/prestd/preStdDtl.do?preStdRegNo={row['bfSpecRgstNo']}"
        )
        prebid_updates.append(msg)

    if bid_updates:
        await channel.send("**오늘의 입찰 공고:**")
        for message in bid_updates:
            await channel.send(message)
    else:
        await channel.send("오늘의 새로운 입찰 공고가 없습니다.")

    if prebid_updates:
        await channel.send("**오늘의 사전 공고:**")
        for message in prebid_updates:
            await channel.send(message)
    else:
        await channel.send("오늘의 새로운 사전 공고가 없습니다.")


bot.run(TOKEN)

# main.py에 추가
from flask import Flask, jsonify
import json

app = Flask(__name__)

DISCORD_WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK_URL')

@app.route('/update_sendOK', methods=['POST'])
def update_sendOK():
    data = request.json
    bid_no = data.get('bidNtceNo')
    file_path = data.get('filePath')

    if not bid_no or not file_path:
        return jsonify({'status': 'error', 'message': 'Missing bid number or file path'}), 400

    df = pd.read_csv(file_path)
    if 'sendOK' not in df.columns:
        df['sendOK'] = 0
    df.loc[df['bidNtceNo'] == bid_no, 'sendOK'] = 4
    df.to_csv(file_path, index=False, encoding='utf-8-sig')

    # Send a message to Discord webhook
    message = f"Updated sendOK to 4 for bid number {bid_no} in {file_path}"
    response = requests.post(DISCORD_WEBHOOK_URL, json={"content": message})

    if response.status_code == 204:
        return jsonify({'status': 'success'}), 200
    else:
        return jsonify({'status': 'error', 'message': 'Failed to send Discord webhook'}), 500

@app.route('/data.json', methods=['GET'])
def get_data():
    with open('data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    response = app.response_class(
        response=json.dumps(data, ensure_ascii=False),
        mimetype='application/json',
        content_type='application/json; charset=utf-8'
    )
    return response

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.getenv("PORT", 8080)))


# .\\.venv\\Scripts\\activate
# python main.py