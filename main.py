import discord
import os
import requests
import json
import time
from discord.ext import commands
from discord.ext import tasks as discordTasks
from dotenv import load_dotenv

bundle_dir = os.path.dirname(os.path.abspath(__file__))
print(bundle_dir)
root_dir = os.path.dirname(bundle_dir)
print(root_dir)
load_dotenv(os.path.join(bundle_dir, ".env"))
print(os.environ.get("TOKEN", "----"))

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)
# client = commands.Bot(command_prefix='dmb')

g_switch = True

def get_token():
	env_dist = os.environ
	token = env_dist.get("TOKEN", "")
	print("\nTOKEN:{0}\n".format(token))
	return token


def get_reserv_info():
	data = {'selDate': "20221107", 'itemCode': "00001", 'discountTypeCode': "00009"}
	response = requests.post("https://hwadamsup.com/mReserve/reserveInfo.do", data = data)

	json_data = json.loads(response.text)
	able_count = 0
	for time_info in json_data["timeList"]:
		able_count += time_info["reQuantity"]

	return(able_count)

@client.event
async def on_ready():
	print('We have logged in as {0.user}'.format(client))


@client.event
async def on_message(message):
	global g_switch
	if message.author == client.user:
		return

	if message.content.startswith('$hello'):
		await message.channel.send('Hello World!')
		embed = discord.Embed(title="화담숲 예약을 원하시나요?", color=0xF1C40F, url='https://hwadamsup.com/mReserve/mReservation.do')
		embed.description = '''안녕하세요,
		11월 17일 예약 가능상황을 실시간으로 알림을 보내는, 알림 전문 봇 '강 봇' 입니다.
		예약 상황을 실시간으로 받아 보시려면 `$start` 를 보내주세요.
		`$start`: 스케줄러 시작
		`$stop`: 스케줄러 중지
		'''

		user = await client.fetch_user(int(message.author.id))
		# user = client.user
		await user.create_dm()
		await user.dm_channel.send(embed=embed)

	if message.content.startswith('$showme'):
		await message.channel.send('Ok!')
		time_list = get_reserv_info()
		await message.channel.send(time_list)

		g_switch = True
		while g_switch:
			await message.channel.send("SWITCH:{0}".format(g_switch))
			time.sleep(1)

	if message.content.startswith("$start"):
		loopMessage.start(message.author.id)
		await message.channel.send("스케줄러가 시작 되었습니다.\n1분 마다 예약상황 체크후 예약가능시 메세지 전송 됩니다.\n스케줄러 멈추실려면 $stop 을 보내주세요.")

	if message.content.startswith("$stop"):
		loopMessage.stop()
		await message.channel.send("스케줄러가 정상적으로 종료되었습니다.")

@discordTasks.loop(minutes = 1.0)
async def loopMessage(user_id):
	able_count = get_reserv_info()
	if able_count > 0: 
		embed = discord.Embed(title="예약자리가 생겼습니다", color=0xF1C40F, url='https://hwadamsup.com/mReserve/mReservation.do')
		embed.description = '''원하신 날짜에 예약 가능합니다. 신속히 예약을 진행 하시길 바랍니다.'''

		user = await client.fetch_user(int(user_id))
		# user = client.user
		await user.create_dm()
		await user.dm_channel.send(embed=embed)


client.run(get_token())

# https://blog.csdn.net/qq_38613380/article/details/119417161
# https://chinese.freecodecamp.org/news/create-a-discord-bot-with-python/