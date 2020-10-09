import subprocess
import sys
import json

subprocess.call('pip install requests -t /tmp/ --no-cache-dir'.split(), stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL)
subprocess.call('pip install sendgrid -t /tmp/ --no-cache-dir'.split(), stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL)
sys.path.insert(1, '/tmp/')

import requests
import logging
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


def lambda_handler(event, context):
    logger.debug(event)
    if event["currentIntent"]['name'] == 'GetWeather':
        city = event["currentIntent"]["slots"]['location']
        API_KEY = 'Your API key'
        BASE_URL = "https://api.openweathermap.org/data/2.5/weather?"
        URL = BASE_URL + "q=" + city + "&appid=" + API_KEY
        response = requests.get(URL)

        if response.status_code == 200:
            # getting data in the json format
            data = response.json()
            # getting the main dict block
            main = data['main']
            # getting temperature
            temperature = main['temp']
            # getting the humidity
            humidity = main['humidity']
            # getting the pressure
            pressure = main['pressure']
            # weather report
            report = data['weather']

            weather_data = {
                'city': city,
                'temperature': temperature,
                'humidity': humidity,
                'pressure': pressure,
                'report': report
            }

            with open("/tmp/weather.txt", 'w') as events_file:
                events_file.write(json.dumps(weather_data))

            return {
                'sessionAttributes': event['sessionAttributes'],
                'dialogAction': {
                    'type': 'ElicitSlot',
                    'intentName': 'SendNotification',
                    'slotToElicit': 'email',
                    'message': {
                        'contentType': 'PlainText',
                        'content': str(weather_data) + '\n\n Please enter your email to get updates'
                    }
                }
            }

        else:
            logger.debug("Error in the HTTP request")
            return {
                'sessionAttributes': event['sessionAttributes'],
                'dialogAction': {
                    'type': 'Close',
                    'fulfillmentState': 'Fulfilled',
                    'message': {
                        'contentType': 'PlainText',
                        'content': 'City not found'
                    }
                }
            }

    elif event["currentIntent"]['name'] == 'SendNotification':
        with open("/tmp/weather.txt", 'r') as file:
            data = file.read().replace('\n', '')

        logger.debug(data)
        toemail = event["currentIntent"]["slots"]['email']
        message = Mail(
            from_email='saritakarki00053@gmail.com',
            to_emails=toemail,
            subject='Weather Updates',
            html_content=data)
        sg = SendGridAPIClient('SENDGRID-KEY')
        response = sg.send(message)

        return {
            'sessionAttributes': event['sessionAttributes'],
            'dialogAction': {
                'type': 'Close',
                'fulfillmentState': 'Fulfilled',
                'message': {
                    'contentType': 'PlainText',
                    'content': 'Weather updates are sent to your email'
                }
            }
        }

# get_weather(None, None)
