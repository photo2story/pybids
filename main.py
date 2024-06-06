import os
from dotenv import load_dotenv
import pandas as pd
import discord
from discord.ext import commands

# 환경 변수에서 API 키를 로드
load_dotenv()

# Discord 설정
TOKEN = os.getenv('DISCORD_APPLICATION_TOKEN')# 환경 변수에서 API 키를 로드(디스코드 가입하고 봇 만들어서 토큰 받아야함)
CHANNEL_ID = os.getenv('DISCORD_CHANNEL_ID')

intents = discord.Intents.default()# 메시지 수신을 위해 intents 설정
intents.messages = True 
intents.message_content = True

bot = commands.Bot(command_prefix='', intents=intents)# 명령어 접두사를 비워두어서 명령어를 입력할 때 접두사를 입력하지 않아도 됨

@bot.event
async def on_ready():
    print(f'Bot이 성공적으로 로그인했습니다: {bot.user.name}')
    channel = bot.get_channel(int(CHANNEL_ID))
    if channel:
        await channel.send(f'Bot이 성공적으로 로그인했습니다: {bot.user.name}')
        await channel.send(f'prebid 100 하수, prebid n 1444267')# 명령어 예시
    else:
        print(f"채널을 찾을 수 없습니다: {CHANNEL_ID}")

@bot.command(name='ping')# 명령어 ping test
async def ping(ctx):
    await ctx.send('pong')

@bot.command(name='prebid')#사전규격 공고 목록 조회
async def prebid(ctx, *, query: str):# 명령어 prebid 100 하수, prebid n 1444267
    if query.startswith('n '):
        prebid_number = query.split(' ')[1]#' '로 나누어서 두번째 값 가져오기
        #나라장터 사전규격 공고 상세페이지 URL
        url = f"https://www.g2b.go.kr:8082/ep/preparation/prestd/preStdDtl.do?preStdRegNo={prebid_number}"
        await ctx.send(url)#메시지로 URL 전송
    else:
        num, keyword = query.split(' ', 1)#' '로 나누어서 두개 값 가져오기
        num = int(num)
        df = pd.read_csv("filtered_prebids_data.csv")#
        filtered_df = df[df['prdctClsfcNoNm'].str.contains(keyword, na=False)]#키워드 품명으로 필터링
        filtered_df = filtered_df.head(num)  # 원하는  갯수만큼 필터링

        if filtered_df.empty:
            await ctx.send(f"No results found for '{keyword}'")
        else:
            messages = []
            for index, row in filtered_df.iterrows():#행 단위로 반복
                asignBdgtAmt = f"{int(row['asignBdgtAmt']):,}원"#금액 천단위 포맷팅
                msg = (
                    f"\n"
                    f"\n[{index + 1}] : 등록번호: {row['bfSpecRgstNo']}\n"
                    f"{row['orderInsttNm']}\n" #기관명
                    f"{row['prdctClsfcNoNm']}\n" #품명
                    f"{asignBdgtAmt}\n"  #예산금액
                    f"{row['rcptDt']}\n" #접수일
                )
                messages.append(msg)#메시지 리스트에 추가

            for message in messages:#
                await ctx.send(message)#메시지 전송

@bot.command(name='bid')
async def bid(ctx, *, query: str):
    if query.startswith('n '):
        bid_number = query.split(' ')[1]
        url = f"http://www.g2b.go.kr:8081/ep/invitation/publish/bidInfoDtl.do?bidno={bid_number}"
        await ctx.send(url)
    else:
        num, keyword = query.split(' ', 1)
        num = int(num)
        df = pd.read_csv("filtered_bids_data.csv")
        filtered_df = df[df['bidNtceNm'].str.contains(keyword, na=False)]
        filtered_df = filtered_df.head(num)  # 원하는 갯수만큼 필터링

        if filtered_df.empty:
            await ctx.send(f"No results found for '{keyword}'")
        else:
            messages = []
            for index, row in filtered_df.iterrows():
                presmptPrce = f"{int(row['presmptPrce']):,}원"
                msg = (
                    f"\n"
                    f"\n[{index + 1}] : 등록번호: {row['bidNtceNo']}\n"
                    f"{row['ntceInsttNm']}\n"#공고기관명
                    f"{row['bidNtceNm']}\n"#공고명
                    f"{presmptPrce}\n"#예정가격
                    f"{row['bidNtceDt']}\n" #공고일
                )
                messages.append(msg)#메시지 리스트에 추가

            for message in messages:
                await ctx.send(message)

bot.run(TOKEN)#봇 실행


# .\\venv\\Scripts\\activate
# python main.py