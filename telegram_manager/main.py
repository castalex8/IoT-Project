import argparse
import logging
from telegram_bot_mqtt import MqttTelegramBot

# set the following variables for the bridge
DEBUG = True

if DEBUG:
    level = logging.DEBUG
else:
    level = logging.INFO  # default value

parser = argparse.ArgumentParser(
        """This script run the telegram bot and all things related to it""")
parser.add_argument('--logs', default='telegram.log',
                    help='File to store logs')
args = parser.parse_args()

logging.getLogger("telegram")
logging.basicConfig(level=level)


if __name__ == '__main__':
    telegram_bot = MqttTelegramBot('localhost')
