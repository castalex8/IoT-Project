import logging
import argparse
import time
from cloud_socket import Cloud
from ai import Ai
import threading
import schedule
import os

# set the following variables for the cloud
DEBUG = True
GMAIL_NAME = "adrenalineDeveloper97"
GMAIL_PASSWD = "GCPDeveloper97"

if DEBUG:
    level = logging.DEBUG
else:
    level = logging.INFO


parser = argparse.ArgumentParser(
    """Cloud script""")
parser.add_argument('--logs', default='cloud.log',
                    help='File to store logs')

args = parser.parse_args()

logging.getLogger('cloud')
logging.basicConfig(level=level)


def run_cloud_socket():
    cloud = Cloud()


def run_ai():
    os.chdir('./files')
    ai = Ai(GMAIL_NAME, GMAIL_PASSWD)

    # Every day/week/month ai.compute_recommendations_for_all() is called
    schedule.every(1).minutes.do(ai.compute_recommendations_for_all)

    # Loop so that the scheduling task
    # keeps on running all time.
    while True:
        # Checks whether a scheduled task
        # is pending to run or not
        schedule.run_pending()
        time.sleep(1)


if __name__ == '__main__':
    cloud_socket_thread = threading.Thread(target=run_cloud_socket)
    cloud_socket_thread.start()

    ai_thread = threading.Thread(target=run_ai)
    ai_thread.start()

