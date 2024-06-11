# Complete Project Details: https://RandomNerdTutorials.com/raspberry-pi-bme280-data-logger/

import smbus2
import bme280
import os
from datetime import date
import time
import pytz

from camera import take_picture
from telegram_bot import send_message_to_telegram_bot, get_messages_from_telegram_bot

# BME280 sensor address (default address)
address = 0x76

# Initialize I2C bus
bus = smbus2.SMBus(1)

# Load calibration parameters
calibration_params = bme280.load_calibration_params(bus, address)

# create a variable to control the while loop
running = True

#telegram bot control
high_humidity_message_enabled = True
last_message_id = 0

# Check if the file exists before opening it in 'a' mode (append mode)
#file_exists = os.path.isfile('sensor_readings_bme280.csv')
#with open('sensor_readings_bme280.csv', 'a') as file:

# Write the header to the file if the file does not exist
#if not file_exists:
#    file.write('Time and Date, temperature (ºC), temperature (ºF), humidity (%), pressure (hPa)\n')

# loop forever
while running:
	try:
		#set filenames for data and image as date
		filename = str(date.today())

		# Read sensor data
		data = bme280.sample(bus, address, calibration_params)

		# Extract temperature, pressure, humidity, and corresponding timestamp
		temperature_celsius = data.temperature
		humidity = data.humidity
		pressure = data.pressure
		timestamp = data.timestamp

		# Adjust timezone
		# Define the timezone you want to use (list of timezones: https://gist.github.com/mjrulesamrat/0c1f7de951d3c508fb3a20b4b0b33a98
		desired_timezone = pytz.timezone('Europe/Berlin')  # Replace with your desired timezone

		# Convert the datetime to the desired timezone
		timestamp_tz = timestamp.replace(tzinfo=pytz.utc).astimezone(desired_timezone)

		# Convert temperature to Fahrenheit
		temperature_fahrenheit = (temperature_celsius * 9/5) + 32

		# Print the readings
		#print(timestamp_tz.strftime('%H:%M:%S %d/%m/%Y') + " Temp={0:0.1f}ºC, Temp={1:0.1f}ºF, Humidity={2:0.1f}%, Pressure={3:0.2f}hPa".format(temperature_celsius, temperature_fahrenheit, humidity, pressure)
		data_filepath = os.path.join('data',filename)+'.csv'
		file_exists= os.path.isfile(data_filepath)
		with open(data_filepath, 'a') as file:
			if not file_exists:
				file.write('Datetime,temperature(°C),temperature(°F),humidity(%),pressure(hPa)\n')
	        	# Save time, date, temperature, humidity, and pressure in .csv file
			file.write(timestamp_tz.strftime('%H:%M:%S %d/%m/%Y') + ', {:.2f}, {:.2f}, {:.2f}, {:.2f}\n'.format(temperature_celsius, temperature_fahrenheit, humidity, pressure))
			file.close()

		# Take picture at 12:00 every day
		image_filename = filename + '.jpg'
		image_filepath = os.path.join('images',image_filename)
		if image_filename not in set(os.listdir("images")) and timestamp_tz.hour >= 12:
			take_picture(image_filepath)
			send_message_to_telegram_bot()

		if high_humidity_message_enabled and humidity > 70:
			send_message_to_telegram_bot('ALERT: High humidity!(>70%)')
			high_humidity_message_enabled = False
		if not high_humidity_message_enabled and humidity < 65:
			send_message_to_telegram_bot('Info: Humidity is low again.(<65%)')
			high_humidity_message_enabled = True

		try:
			newest_message = get_messages_from_telegram_bot()['result'][-1]# ['message']['text']
			message_text = newest_message['message']['text']
			message_id = newest_message['message']['message_id']
			if message_text == 'Status' and message_id != last_message_id:
				send_message_to_telegram_bot(f'Temparature: {round(temperature_celsius, 2)}°C, Humidity: {round(humidity, 2)}%, Pressure: {round(pressure, 2)}hPa')
				last_message_id = message_id
		except Exception as e:
			pass#print(str(e))

		time.sleep(10)

	except KeyboardInterrupt:
		print('Program stopped')
		running = False
	except Exception as e:
		with open('error.txt', 'a') as file:
			file.write(timestamp_tz.strftime('%H:%M:%S %d/%m/%Y') + ' | error: ' + str(e))
		print('An unexpected error occurred:', str(e))
		running = False
