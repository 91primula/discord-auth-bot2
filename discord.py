# ────────────────────────────────
# ✅ 필요 모듈 설치
# ────────────────────────────────
# pip install discord.py python-dotenv asyncio

import os
import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv
import asyncio

# ────────────────────────────────
# ✅ 환경 변수 로드
# ────────────────────────────────
load_dotenv()
TOKEN = os.getenv("DISCORD_BOT_TOKEN")  # 봇 토큰
GUILD_ID = int(os.getenv("DISCORD_GUILD_ID"))  # 서버 ID
CHANNEL_ID = int(os.getenv("DISCORD_CHANNEL_ID"))  # 채널 ID
ROLE_NAME = "쟁탈원"
TOKEN = os.getenv("DISCORD_CORRECT_CODE")  # 정답

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ────────────────────────────────
# ✅ 메시지 이벤트 처리
# ────────────────────────────────
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    # 채널 확인
    if message.channel.id != CHANNEL_ID:
        return

    # 맞는 코드 입력
    if message.content.strip() == CORRECT_CODE:
        # 역할 부여
        guild = bot.get_guild(GUILD_ID)
        role = discord.utils.get(guild.roles, name=ROLE_NAME)
        if role and isinstance(message.author, discord.Member):
            await message.author.add_roles(role)
            await message.channel.send(f"{message.author.mention}님, 역할이 부여되었습니다!", delete_after=2)
        await message.delete()  # 메시지 즉시 삭제
    else:
        # 틀린 코드 입력
        await message.channel.send(f"{message.author.mention} 잘못된 답입니다.", delete_after=10)

    await bot.process_commands(message)

# ────────────────────────────────
# ✅ 5분마다 메시지 정리 (고정 메시지 제외)
# ────────────────────────────────
@tasks.loop(minutes=5)
async def cleanup_channel():
    channel = bot.get_channel(CHANNEL_ID)
    if not channel:
        return
    async for msg in channel.history(limit=100):
        if msg.pinned:
            continue
        try:
            await msg.delete()
        except:
            pass

@bot.event
async def on_ready():
    print(f"Bot is ready! Logged in as {bot.user}")
    cleanup_channel.start()

bot.run(TOKEN)
