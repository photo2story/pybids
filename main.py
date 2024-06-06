import os
from dotenv import load_dotenv
import pandas as pd
import discord
from discord.ext import commands, tasks

# Load environment variables
load_dotenv()

# Discord settings
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
                    f"\n"
                    f"\n[{index + 1}] : 등록번호: {row['bfSpecRgstNo']}\n"
                    f"{row['orderInsttNm']}\n"
                    f"{row['prdctClsfcNoNm']}\n"
                    f"{asignBdgtAmt}\n"
                    f"{row['rcptDt']}\n"
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
                    f"\n"
                    f"\n[{index + 1}] : 등록번호: {row['bidNtceNo']}\n"
                    f"{row['ntceInsttNm']}\n"
                    f"{row['bidNtceNm']}\n"
                    f"{presmptPrce}\n"
                    f"{row['bidNtceDt']}\n"
                )
                messages.append(msg)

            for message in messages:
                await ctx.send(message)

# Define the update task
@tasks.loop(hours=24)  # Update data every 24 hours
async def update_data_task():
    from update_data import update_prebids_data, update_bids_data
    update_prebids_data()
    update_bids_data()

bot.run(TOKEN)


# .\\venv\\Scripts\\activate
# python main.py