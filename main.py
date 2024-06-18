# main.py

from flask import Flask, request, jsonify
from threading import Thread
import os
import pandas as pd
from dotenv import load_dotenv
import discord
from discord.ext import commands, tasks
import datetime
import subprocess
import csv
import requests  # 디스코드 웹훅 사용을 위해 추가

os.environ['PYTHONIOENCODING'] = 'UTF-8'

# 가상 환경 활성화 경로
venv_path = os.path.join(os.path.dirname(__file__), '.venv')
site_packages_path = os.path.join(venv_path, 'Lib', 'site-packages')

# 환경 변수에서 API 키를 로드
load_dotenv()

app = Flask(__name__)

# 디스코드 웹훅 URL
DISCORD_WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK_URL')

@app.route('/')
def home():
    return "I'm alive"

@app.route('/update_sendok', methods=['POST'])
def update_sendok():
    item_to_update = request.json
    print(f"Received update request for item: {item_to_update}")
    if 'opengDt' in item_to_update:
        update_sendok_in_csv(bidwin_file, item_to_update)
    elif 'bidNtceDt' in item_to_update:
        update_sendok_in_csv(bids_file, item_to_update)
    elif 'rcptDt' in item_to_update:
        update_sendok_in_csv(prebids_file, item_to_update)
    return jsonify({'status': 'success'})

def update_sendok_in_csv(file_path, item_to_update):
    df = pd.read_csv(file_path)
    if 'opengDt' in item_to_update:
        condition = (df['opengDt'] == item_to_update['opengDt']) & (df['bidNtceNo'] == item_to_update['bidNtceNo'])
    elif 'bidNtceDt' in item_to_update:
        condition = (df['bidNtceDt'] == item_to_update['bidNtceDt']) & (df['bidNtceNo'] == item_to_update['bidNtceNo'])
    elif 'rcptDt' in item_to_update:
        condition = (df['rcptDt'] == item_to_update['rcptDt']) & (df['bfSpecRgstNo'] == item_to_update['bfSpecRgstNo'])

    df.loc[condition, 'sendOK'] = 1
    df.to_csv(file_path, index=False, encoding='utf-8-sig')

    # 디스코드 웹훅 알림
    send_discord_webhook(f"Updated sendOK for: {item_to_update}")

def send_discord_webhook(message):
    data = {"content": message}
    response = requests.post(DISCORD_WEBHOOK_URL, json=data)
    if response.status_code != 204:
        print(f"Failed to send webhook: {response.status_code}, {response.text}")

def run():
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 8080)))

def keep_alive():
    server = Thread(target=run)
    server.start()

keep_alive()

# Discord 설정
TOKEN = os.getenv('DISCORD_APPLICATION_TOKEN')
CHANNEL_ID = os.getenv('DISCORD_CHANNEL_ID')

intents = discord.Intents.default()
intents.messages = True
client = discord.Client(intents=intents)

bot = commands.Bot(command_prefix='', intents=intents)

# 나머지 Discord 관련 코드...

if __name__ == "__main__":
    bot.run(TOKEN)
    # app.run(host='127.0.0.1', port=int(os.getenv('PORT', 8080)))

    # app.run(host='127.0.0.1', port=int(os.getenv('PORT', 8080)))

# .\\.venv\\Scripts\\activate
# python main.py