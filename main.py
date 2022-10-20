import discord
import os
import requests
import json
import time
from discord.ext import commands
from discord.ext import tasks as discordTasks
from dotenv import load_dotenv

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

# 환경변수 읽기
def load_environments():
	# TOKEN 을 명문으로 표기하고 공개레포지토리에 올리면 디스코드에서 경고문자 오고 토큰을 강제 비활성화 시킴. 
	# 그래서 레포지토리에 안 올라가는 ./.env 파일 별도 만들어서 읽어오기로
	# .env 파일 격식:
	# ---
	# TOKEN=YOUR_BOTS_TOKEN
	# ---
	bundle_dir = os.path.dirname(os.path.abspath(__file__))
	root_dir = os.path.dirname(bundle_dir)
	load_dotenv(os.path.join(bundle_dir, ".env"))

	print(os.environ.get("TOKEN", "read token error: .env 파일에서 토큰 읽어오기를 실패 하였습니다."))


# 환경변수 에서 토큰 가져오기
def get_token():
	env_dist = os.environ
	token = env_dist.get("TOKEN", "")
	print("\nTOKEN:{0}\n".format(token))
	return token


# 11월07일 예약가능 자리 취합
def get_reserv_info():
	data = {'selDate': "20221107", 'itemCode': "00001", 'discountTypeCode': "00009"}
	response = requests.post("https://hwadamsup.com/mReserve/reserveInfo.do", data = data)
	print(response.text)
	json_data = json.loads(response.text)
	able_count = 0
	for time_info in json_data["timeList"]:
		able_count += time_info["reQuantity"]

	return(able_count)

# 봇 준비 시 콜백
@client.event
async def on_ready():
	print('We have logged in as {0.user}'.format(client))


# 사용자가 봇에 보낸 메세지 에 따라 반응 콜백
@client.event
async def on_message(message):
	if message.author == client.user: # 봇이 자신의 메세지에 반응하지 않도록
		return

	if message.content.startswith('$hello'):
		await message.channel.send('Hello World!') # 문자 받은 채널로 회신 보냄
		# 임베드 메세지 구성
		embed = discord.Embed(title="화담숲 예약을 원하시나요?", color=0xF1C40F, url='https://hwadamsup.com/mReserve/reserveMain.do')
		embed.description = '''안녕하세요,
		11월 17일 예약 가능상황을 실시간으로 알림을 보내는, 알림 전문 봇 '강 봇' 입니다.
		예약 상황을 실시간으로 받아 보시려면 `$start` 를 보내주세요.
		`$start`: 스케줄러 시작
		`$stop`: 스케줄러 중지
		'''

		user = await client.fetch_user(int(message.author.id))
		await user.create_dm()
		await user.dm_channel.send(embed=embed)

	if message.content.startswith('$showme'):
		await message.channel.send('Ok!')
		able_count = get_reserv_info()
		await message.channel.send(able_count)

	# 스케줄러 시작
	if message.content.startswith("$start"):
		loopMessage.start(message.author.id)
		await message.channel.send("스케줄러가 시작 되었습니다.\n1분 마다 예약상황 체크후 예약가능시 메세지 전송 됩니다.\n스케줄러 멈추실려면 $stop 을 보내주세요.")

	# 스케줄러 종료
	if message.content.startswith("$stop"):
		loopMessage.stop()
		await message.channel.send("스케줄러가 정상적으로 종료되었습니다.")

# discord.py 에서 지원 해준 스케줄러
@discordTasks.loop(minutes = 1.0)
async def loopMessage(user_id):
	able_count = get_reserv_info()
	if able_count > 0: 
		embed = discord.Embed(title="예약자리가 생겼습니다", color=0xF1C40F, url='https://hwadamsup.com/mReserve/reserveMain.do')
		embed.description = '''원하신 날짜에 예약 가능합니다. 신속히 예약을 진행 하시길 바랍니다.'''

		# 스케줄러 시작하면 채널로 메세지 보내는거 아니라 사용자 한테 dm 으로 소식 보낸다
		user = await client.fetch_user(int(user_id))
		await user.create_dm()
		await user.dm_channel.send(embed=embed)

# 시작
load_environments()
client.run(get_token())