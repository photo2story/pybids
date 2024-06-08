# main.py

import os
from dotenv import load_dotenv
import pandas as pd
import discord
from discord.ext import commands, tasks
import datetime

# 환경 변수에서 API 키를 로드
load_dotenv()

# Discord 설정
TOKEN = os.getenv('DISCORD_APPLICATION_TOKEN')
CHANNEL_ID = os.getenv('DISCORD_CHANNEL_ID')

intents = discord.Intents.default()
intents.messages = True
client = discord.Client(intents=intents)

bot = commands.Bot(command_prefix='', intents=intents)

@bot.event
async def on_ready():
    print(f'Bot이 성공적으로 로그인했습니다: {bot.user.name}')
    channel = bot.get_channel(int(CHANNEL_ID))
    if channel:
        await channel.send(f'Bot이 성공적으로 로그인했습니다: {bot.user.name}')
        await channel.send("사용 가능한 명령어:\n- `bid <검색어>`: 공고 검색\n- `prebid <검색어>`: 사전 공고 검색\n- `show <YYYYMMDD>`: 특정 날짜의 새로운 공고 검색")

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
        filtered_df = filtered_df.head(num)

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

@bot.command(name='show')
async def show(ctx, date: str):
    specific_date = datetime.datetime.strptime(date, "%Y%m%d").date()
    
    # 필터링된 공고
    bid_updates = []
    prebid_updates = []

    # Bid updates
    df_bids = pd.read_csv("filtered_bids_data.csv")
    df_bids['bidNtceDt'] = pd.to_datetime(df_bids['bidNtceDt'], errors='coerce').dt.date
    df_bids['sendOK'] = df_bids['sendOK'].fillna(0)
    new_bids = df_bids[(df_bids['bidNtceDt'] == specific_date) & (df_bids['sendOK'] == 0)]
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
        df_bids.loc[df_bids['bidNtceNo'] == row['bidNtceNo'], 'sendOK'] = 1

    # Prebid updates
    df_prebids = pd.read_csv("filtered_prebids_data.csv")
    df_prebids['rcptDt'] = pd.to_datetime(df_prebids['rcptDt'], errors='coerce').dt.date
    df_prebids['sendOK'] = df_prebids['sendOK'].fillna(0)
    new_prebids = df_prebids[(df_prebids['rcptDt'] == specific_date) & (df_prebids['sendOK'] == 0)]
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
        df_prebids.loc[df_prebids['bfSpecRgstNo'] == row['bfSpecRgstNo'], 'sendOK'] = 1

    if bid_updates:
        await ctx.send("**해당 날짜의 입찰 공고:**")
        for message in bid_updates:
            await ctx.send(message)
    else:
        await ctx.send("해당 날짜의 새로운 입찰 공고가 없습니다.")

    if prebid_updates:
        await ctx.send("**해당 날짜의 사전 공고:**")
        for message in prebid_updates:
            await ctx.send(message)
    else:
        await ctx.send("해당 날짜의 새로운 사전 공고가 없습니다.")
    
    df_bids.to_csv("filtered_bids_data.csv", index=False, encoding='utf-8-sig')
    df_prebids.to_csv("filtered_prebids_data.csv", index=False, encoding='utf-8-sig')

bot.run(TOKEN)

# .\\venv\\Scripts\\activate
# python main.py