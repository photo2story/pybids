# main.py

import os
import pandas as pd
from dotenv import load_dotenv
import discord
from discord.ext import commands, tasks
import datetime
import subprocess
from get_update_bids import get_bid_updates, get_prebid_updates, get_bidwin_updates, save_updated_dataframes

# 환경 변수에서 API 키를 로드
load_dotenv()

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
    scripts = ["get_prebids.py", "get_bids.py", "get_bidwin.py", "export_json.py"]

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(fetch_data_and_update, script) for script in scripts]
        for future in concurrent.futures.as_completed(futures):
            try:
                future.result()
            except Exception as e:
                print(f"An error occurred: {e}")

    channel = bot.get_channel(int(CHANNEL_ID))
    if channel:
        today = datetime.date.today()
        yesterday = today - datetime.timedelta(days=1)
        await show_updates(channel, today)
        await show_updates(channel, yesterday)


def fetch_data_and_update(script_name):
    try:
        result = subprocess.run(['python', script_name], capture_output=True, text=True, encoding='utf-8')
        if result.returncode == 0:
            print(f"Script {script_name} executed successfully.")
        else:
            print(f"Script {script_name} failed with status code {result.returncode}.")
    except Exception as e:
        print(f"An error occurred while executing {script_name}: {e}")

async def send_daily_updates():
    channel = bot.get_channel(int(CHANNEL_ID))
    specific_date_str = "20240607"  # 특정 날짜로 설정
    specific_date = datetime.datetime.strptime(specific_date_str, "%Y%m%d").date()
    
    # 필터링된 공고
    bid_updates = []
    prebid_updates = []

    # Bid updates
    df_bids = pd.read_csv("filtered_bids_data.csv")
    df_bids['bidNtceDt'] = pd.to_datetime(df_bids['bidNtceDt']).dt.date
    new_bids = df_bids[df_bids['bidNtceDt'] == specific_date]
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
    new_prebids = df_prebids[df_prebids['rcptDt'] == specific_date]
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


# .\\venv\\Scripts\\activate
# python main.py