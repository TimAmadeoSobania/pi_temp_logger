import requests
import json
from time import sleep
with open("/home/tim/Desktop/Projects/bathroom_sensors/telegram_api.json","r") as file:
	api_data = json.load(file)

def send_message_to_telegram_bot(message:str="Script is still runnning", retry:int=6):
	try:
		url = f"https://api.telegram.org/bot{api_data['TOKEN']}/sendMessage?chat_id={api_data['CHAT_ID']}&text={message}"
		requests.get(url)
	except Exception:
		print(f"Failed to send message, retrying in 10 seconds (retry{retry}).")
		sleep(10)
		send_message_to_telegram_bot(retry-1)

def get_messages_from_telegram_bot():
	try:
		url = f"https://api.telegram.org/bot{api_data['TOKEN']}/getUpdates"
		update = requests.get(url).json()
		return update
	except Exception:
		return Exception

