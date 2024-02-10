import logging
import json
import azure.functions as func
from datetime import datetime, timezone
import requests
from bs4 import BeautifulSoup
from opencensus.ext.azure.log_exporter import AzureLogHandler
import os
#https://pypi.org/project/opencensus-ext-azure/

logger = logging.getLogger(__name__)
azure_handler = AzureLogHandler(connection_string=os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING", 'default'))
logger.addHandler(azure_handler)

def parse_request_data(url):
    response = requests.get(url)
    html_content = response.text

    # Parse HTML using BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')

    # Extract the number of logged-in users
    online_users_text = soup.find(id="online").get_text()
    online_users_number = int("".join(filter(str.isdigit, online_users_text)))

    return online_users_number

def main(mytimer: func.TimerRequest) -> None:
    utc_timestamp = datetime.utcnow().replace(tzinfo=timezone.utc)
    date_str = utc_timestamp.strftime('%Y-%m-%d')
    weekday_str = utc_timestamp.strftime('%A') 

    url = 'https://www.hattrick.org/pl/'
    
    try:
        active_users = parse_request_data(url)
    except Exception as e:
        logging.error(f'{str(e)}')
        active_users = 0

    custom_dimensions = {
        'active_users': str(active_users),
        'date': date_str,
        'check_time': utc_timestamp.strftime('%Y-%m-%dT%H:%M:%S'),
        'weekday': weekday_str
    }
    logger.info('Hattrick active users new 2', extra={'custom_dimensions': custom_dimensions})