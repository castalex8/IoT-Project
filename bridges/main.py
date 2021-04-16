import logging
import argparse
import time
from bridge_locker import LockerBridge
from bridge_mqtt import MqttBridge
from send_to_cloud import Sender
import threading
import schedule

# set the following variables for the bridge
DEBUG = True
bridge_id = '1'  # must be a string and must be unique for each bridge
state = 'italy'
region = 'emilia-romagna'

if DEBUG:
    level = logging.DEBUG
else:
    level = logging.INFO

parser = argparse.ArgumentParser(
    """This script run the bridge and all things related to it""")
parser.add_argument('--video_source', type=int, default=1,
                    help='Video source where read QR code and barcode, in general 0 or 1')
parser.add_argument('--logs', default='bridge.log',
                    help='File to store logs')
parser.add_argument('--broker_address', default='localhost',
                    help='Address of the broker')
parser.add_argument('--bridge_id', default=bridge_id,
                    help='Identifier of the bridge, it must be  unique for each bridge')
parser.add_argument('--state', default=state,
                    help='State where is located the bridge')
parser.add_argument('--region', default=region,
                    help='Region where is located the bridge')

args = parser.parse_args()

logging.getLogger('bridge')
logging.basicConfig(level=level)

db_name = str(args.bridge_id) + '.db'

mqtt_bridge = MqttBridge(args.state, args.region, args.bridge_id, db_name, args.broker_address)
locker_bridge = LockerBridge(args.state, args.region, args.bridge_id, db_name, args.video_source)


def run_mqtt_bridge():
    mqtt_bridge.loop()


def run_locker_bridge():
    locker_bridge.loop()
    mqtt_bridge.disconnect()


def run_send_to_cloud_thread():
    sender = Sender(db_name)
    schedule.every(3).minutes.do(sender.send_all)

    # Loop so that the scheduling task
    # keeps on running all time.
    while True:
        # Checks whether a scheduled task
        # is pending to run or not
        schedule.run_pending()
        time.sleep(1)


if __name__ == '__main__':
    mqtt_thread = threading.Thread(target=run_mqtt_bridge)
    mqtt_thread.start()

    time.sleep(1)

    locker_thread = threading.Thread(target=run_locker_bridge)
    locker_thread.start()

    send_to_ai_thread = threading.Thread(target=run_send_to_cloud_thread)
    send_to_ai_thread.start()
