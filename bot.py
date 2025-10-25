import os
import asyncio
from discord.ext import commands, tasks
from dotenv import load_dotenv
import discord
from datetime import datetime, timedelta

# ────────────────────────────────
# ✅ 환경 변수 로드
# ────────────────────────────────
load_dotenv()
TOKEN = os.getenv("DISCORD_BOT_TOKEN")         # 봇 토큰
CORRECT_CODE = os.getenv("DISCORD_CORRECT")    # 정답 코드
GUILD_ID = int(os.getenv("DISCORD_GUILD_ID"))  # 서버 ID
TARGET_CHANNEL_ID = int(os.getenv("DISCORD_CHANNEL_ID"))  # 채널 ID
ROLE_NAME = os.getenv("DISCORD_ROLE_NAME", "쟁탈원")      # 부여할 역할

# ────────────────────────────────
# ✅ 봇 세팅
# ────────────────────────────────
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# 마지막 활동 시간 저장
last_action_time = datetime.utcnow()

# ────────────────────────────────
# ✅ 메시지 삭제 반복 작업
# ────────────────────────────────
@tasks.loop(seconds=60)  # 1분마다 체크
async def cleanup_messages():
    global last_action_time
    now = datetime.utcnow()
    if (now - last_action_time) > timedelta(minutes=5):
        channel = bot.get_channel(TARGET_CHANNEL_ID)
        if channel:
            # 고정 메시지를 제외하고 삭제
            pinned = await channel.pins()
            pinned_ids = [msg.id for msg in pinned]
            async for msg in channel.history(limit=200):
                if msg.id not in pinned_ids:
                    await msg.delete()
            last_action_time = now  # 마지막 청소 시간 갱신

# ────────────────────────────────
# ✅ 메시지 이벤트
# ────────────────────────────────
@bot.event
async def on_message(message):
    global last_action_time
    if message.author.bot:
        return

    if message.channel.id != TARGET_CHANNEL_ID:
        return

    last_action_time = datetime.utcnow()

    if message.content.strip() == CORRECT_CODE:
        # 역할 부여
        guild = bot.get_guild(GUILD_ID)
        role = discord.utils.get(guild.roles, name=ROLE_NAME)
        if role:
            await message.author.add_roles(role)
            notice = await message.channel.send(f"{message.author.mention} 역할이 부여되었습니다!")
            await asyncio.sleep(2)
            await notice.delete()
        await message.delete()  # 정답 메시지 즉시 삭제
    else:
        await message.channel.send(f"{message.author.mention} 잘못된 답입니다!")

# ────────────────────────────────
# ✅ 봇 준비 완료 이벤트
# ────────────────────────────────
@bot.event
async def on_ready():
    print(f"Bot logged in as {bot.user}")
    cleanup_messages.start()

# ────────────────────────────────
# ✅ 봇 실행
# ────────────────────────────────
bot.run(TOKEN)
