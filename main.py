import os
from dotenv import load_dotenv
import pandas as pd
import discord
from discord.ext import commands, tasks
import subprocess
import json
import datetime

# 환경 변수에서 API 키를 로드
load_dotenv()

# Discord 설정
TOKEN = os.getenv('DISCORD_APPLICATION_TOKEN')
CHANNEL_ID = os.getenv('DISCORD_CHANNEL_ID')

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

bot = commands.Bot(command_prefix='', intents=intents)

@bot.event
async def on_ready():
    print(f'Bot이 성공적으로 로그인했습니다: {bot.user.name}')
    channel = bot.get_channel(int(CHANNEL_ID))
    if channel:
        await channel.send(f'Bot이 성공적으로 로그인했습니다: {bot.user.name}')
        await channel.send(f'prebid 100 하수, prebid n 1444267')
    else:
        print(f"채널을 찾을 수 없습니다: {CHANNEL_ID}")
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
        filtered_df = filtered_df.head(num)  # Filter the desired number of rows

        if filtered_df.empty:
            await ctx.send(f"No results found for '{keywords}'")
        else:
            messages = []
            for index, row in filtered_df.iterrows():
                asignBdgtAmt = f"{int(row['asignBdgtAmt']):,}원"
                msg = (
                    f"\n[{index + 1}]\n"
                    f"\n등록번호: {row['bfSpecRgstNo']}\n"
                    f"{row['orderInsttNm']}\n"
                    f"{row['prdctClsfcNoNm']}\n"
                    f"{asignBdgtAmt}\n"
                    f"{row['rcptDt']}\n"
                    f"https://www.g2b.go.kr:8082/ep/preparation/prestd/preStdDtl.do?preStdRegNo={row['bfSpecRgstNo']}\n"
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
        filtered_df = filtered_df.head(num)  # Filter the desired number of rows

        if filtered_df.empty:
            await ctx.send(f"No results found for '{keywords}'")
        else:
            messages = []
            for index, row in filtered_df.iterrows():
                presmptPrce = f"{int(row['presmptPrce']):,}원"
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

# Define the update task
@tasks.loop(hours=24)  # Update data every 24 hours
async def update_data_task():
    await update_bids_data()
    await update_prebids_data()

async def update_bids_data():
    try:
        result = subprocess.run(['python', 'get_bids.py'], capture_output=True, text=True, encoding='utf-8')
        if result.returncode == 0:
            print(f"Script get_bids.py executed successfully.")
            # 당일 변동 사항 메시징
            df = pd.read_csv("filtered_bids_data.csv")
            today_str = datetime.datetime.now().strftime('%Y-%m-%d')
            today_bids = df[df['bidNtceDt'].str.startswith(today_str)]
            if not today_bids.empty:
                messages = []
                for index, row in today_bids.iterrows():
                    presmptPrce = f"{int(row['presmptPrce']):,}원"
                    msg = (
                        f"\n# 당일 공고: {datetime.datetime.now().strftime('%Y.%m.%d %H:%M')}\n"
                        f"# {row['bidNtceNm']} 용역이 공고되었습니다.\n"
                        f"# {presmptPrce}\n"
                        f"# http://www.g2b.go.kr:8081/ep/invitation/publish/bidInfoDtl.do?bidno={row['bidNtceNo']}\n"
                    )
                    messages.append(msg)
                
                channel = bot.get_channel(int(CHANNEL_ID))
                if channel:
                    for message in messages:
                        await channel.send(message)
        else:
            print(f"Script get_bids.py failed with status code {result.returncode}.")
    except Exception as e:
        print(f"An error occurred while executing get_bids.py: {e}")

async def update_prebids_data():
    try:
        result = subprocess.run(['python', 'get_prebids.py'], capture_output=True, text=True, encoding='utf-8')
        if result.returncode == 0:
            print(f"Script get_prebids.py executed successfully.")
            # 당일 변동 사항 메시징
            df = pd.read_csv("filtered_prebids_data.csv")
            today_str = datetime.datetime.now().strftime('%Y-%m-%d')
            today_prebids = df[df['rcptDt'].str.startswith(today_str)]
            if not today_prebids.empty:
                messages = []
                for index, row in today_prebids.iterrows():
                    asignBdgtAmt = f"{int(row['asignBdgtAmt']):,}원"
                    msg = (
                        f"\n# 당일 공고: {datetime.datetime.now().strftime('%Y.%m.%d %H:%M')}\n"
                        f"# {row['prdctClsfcNoNm']} 용역이 사전공고되었습니다.\n"
                        f"# {asignBdgtAmt}\n"
                        f"# https://www.g2b.go.kr:8082/ep/preparation/prestd/preStdDtl.do?preStdRegNo={row['bfSpecRgstNo']}\n"
                    )
                    messages.append(msg)
                
                channel = bot.get_channel(int(CHANNEL_ID))
                if channel:
                    for message in messages:
                        await channel.send(message)
        else:
            print(f"Script get_prebids.py failed with status code {result.returncode}.")
    except Exception as e:
        print(f"An error occurred while executing get_prebids.py: {e}")

bot.run(TOKEN)


# .\\venv\\Scripts\\activate
# python main.py