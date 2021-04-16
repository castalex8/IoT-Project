import paho.mqtt.client as mqtt
import logging
import time

from telegram_bot import TelegramBot

logging.getLogger('telegram.mqtt')


class MqttTelegramBot(TelegramBot):

    def __init__(self, mqtt_broker_address):
        self.dict_of_rc = {}
        self.client = mqtt.Client(client_id='client_bot', clean_session=True)
        self.client.enable_logger()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        try:
            self.client.connect(mqtt_broker_address)
        except ConnectionRefusedError:
            logging.critical("[__init__] Connection refused by the mqtt broker! The broker are running?")
            exit(1)
        self.client.loop_start()
        super().__init__()

    @staticmethod
    def on_connect(mqtt_client_id, mqtt_userdata, flags, rc):
        logging.info('[on_connect] Connect with the Broker')

    def on_message(self, mqtt_client_id, mqtt_userdata, msg) -> None:
        logging.info('[on_message] ' + msg.topic + " " + str(msg.payload))
        return_code = msg.payload.decode().split()[1]
        remote_client_id = msg.topic.split("/")[-1]

        if return_code == '[Y]':
            self.dict_of_rc[remote_client_id] = msg.payload.decode().split()[0]
        elif return_code == '[N]':
            self.dict_of_rc[remote_client_id] = 0
        else:
            self.dict_of_rc[remote_client_id] = msg.payload.decode().split()[0]

    def __del__(self):
        self.client.loop_stop()

    def find_bridge(self, client_id: int, user_data: dict) -> None:
        state, region = user_data['state'], user_data['region']
        sub_topic = f'world/{state}/{region}/clients/{client_id}'
        self.client.subscribe(sub_topic)

        pub_topic = f'world/{state}/{region}/bridges'
        payload = str(client_id)
        self.client.publish(pub_topic, payload)

    def find_book(self, client_id: int, user_data: dict, title: str) -> None:
        state, region, bridge_id = user_data['state'], user_data['region'], user_data['bridge']
        sub_topic = f'world/{state}/{region}/clients/{client_id}'
        self.client.subscribe(sub_topic)

        pub_topic = f'world/{state}/{region}/bridges/{bridge_id}'
        payload = str(client_id) + " BOOK " + title + ""
        self.client.publish(pub_topic, payload)
        logging.info(f'[find_book] mqtt msg PUBLISHED: {payload}')

    def sign_in(self, client_id: int, user_data: dict, name: str, email: str) -> None:
        state, region, bridge_id = user_data['state'], user_data['region'], user_data['bridge']
        sub_topic = f'world/{state}/{region}/clients/{client_id}'
        self.client.subscribe(sub_topic)

        pub_topic = f'world/{state}/{region}/bridges/{bridge_id}'
        payload = str(client_id) + " SIGN_IN \"" + name + "\" " + "\"" + email + "\""
        self.client.publish(pub_topic, payload)
        logging.info(f'[sign_in] mqtt msg PUBLISHED: {payload}')

    def freespace(self, client_id: int, user_data: dict):
        state, region, bridge_id = user_data['state'], user_data['region'], user_data['bridge']
        sub_topic = f'world/{state}/{region}/clients/{client_id}'
        self.client.subscribe(sub_topic)

        pub_topic = f'world/{state}/{region}/bridges/{bridge_id}'
        payload = str(client_id) + " FREESPACE"
        self.client.publish(pub_topic, payload)
        logging.info(f'[freespace] mqtt msg PUBLISHED: {payload}')

    def reserve_book(self, client_id: int, user_data: dict, title: str):
        state, region, bridge_id = user_data['state'], user_data['region'], user_data['bridge']
        sub_topic = f'world/{state}/{region}/clients/{client_id}'
        self.client.subscribe(sub_topic)

        pub_topic = f'world/{state}/{region}/bridges/{bridge_id}'
        payload = str(client_id) + " RESERVE " + title + ""
        self.client.publish(pub_topic, payload)
        logging.info(f'[reserve_book] mqtt msg PUBLISHED: {payload}')

    def last_rc(self, client_id: int) -> int:
        time.sleep(0.3)  # a timeout is necessary to receive the callback on_message
        if self.dict_of_rc.get(str(client_id)) is None:
            logging.info('[last_rc] : 0')
            return 0
        logging.info(f'[last_rc] : {self.dict_of_rc.get(str(client_id))}')
        return self.dict_of_rc.get(str(client_id))
