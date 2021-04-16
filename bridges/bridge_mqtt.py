import paho.mqtt.client as mqtt
from bridge_locker import *
from bridge import Bridge
import logging


logging.getLogger('bridge.mqtt')


def on_connect(client_id, userdata, flags, rc):
    logging.info('[(MqttBridge) on_connect] Connect with the Broker')


def on_message(client_id, userdata, msg):
    logging.info('[(MqttBridge) on_message] ' + msg.topic + " " + str(msg.payload))


class MqttBridge(Bridge):
    def __init__(self, state, region, bridge_id, db_name, mqtt_broker_address):
        super().__init__(state, region, bridge_id)
        self.dict_of_rc = {}
        self.db_name = db_name
        self.locker = SqliteLocker(self.db_name)
        self.client = mqtt.Client(client_id=f'bridge{self.bridge_id}', clean_session=True)
        self.client.enable_logger()

        self.client.on_connect = on_connect
        self.client.on_message = on_message

        self.client.connect(mqtt_broker_address)

        # a subscribe to communicate with only this bridge, for client-bridge and bridge-bridge communication
        topic = f'world/{state}/{region}/bridges/{bridge_id}'
        self.client.message_callback_add(topic, self.on_message_from_client)
        self.client.subscribe(topic)

        # a subscribe to check if clients try to find bridges in a specific area
        topic = f'world/{state}/{region}/bridges'
        self.client.message_callback_add(topic, self.on_bridges_query)
        self.client.subscribe(topic)

        # subscribe for comunication bridge - bridge
        # book retrieval
        topic = f'world/{state}/{region}/bridges/book'
        self.client.message_callback_add(topic, self.on_book_query)
        self.client.subscribe(topic)

        # find bridge with free space
        topic = f'world/{state}/{region}/bridges/freespace'
        self.client.message_callback_add(topic, self.on_freespace_query)
        self.client.subscribe(topic)

        '''# find bridge for a specific client
        topic = f'world/{state}/{region}/bridges/client'
        self.client.message_callback_add(topic, self.on_client_query)
        self.client.subscribe(topic)'''

    def loop(self):
        self.client.loop_forever()

    def disconnect(self):
        self.client.disconnect()

    def ask_freespace_to_other(self, client_id):
        logging.info('[ask_freespace_to_other bridge]')
        topic = f'world/{self.state}/{self.region}/bridges/freespace'
        payload = str(client_id)
        self.client.publish(topic, payload)

    def ask_book_to_other(self, client_id, title):
        logging.info('[ask_book_to_other bridge]')
        topic = f'world/{self.state}/{self.region}/bridges/book'
        payload = str(client_id) + " " + title
        self.client.publish(topic, payload)

    def on_message_from_client(self, client_id, userdata, msg):
        logging_msg = '[on_message_from_client]'

        msg_list = msg.payload.decode().split()
        remote_client_id = msg_list[0]
        logging_msg = f'[on_message_from_client ({remote_client_id}) mqtt msg PUBLISHED:]'
        topic = f'world/{self.state}/{self.region}/clients/{remote_client_id}'
        payload = self.bridge_id
        # command = {SIGN_IN, FREESPACE, BOOK , RESERVE}
        command = msg_list[1]
        if command == 'SIGN_IN':
            name = msg_list[2]
            email = msg_list[3]
            if self.locker.add_client(remote_client_id, name, email):
                payload += f' [Y] bridge added client {remote_client_id} {name} {email}'
            else:
                payload += f' [N] bridge NOT added client {remote_client_id} {name} {email}'
            self.client.publish(topic, payload)
            logging.info(logging_msg + payload)
        elif command == 'FREESPACE':
            if self.locker.check_free_space():
                payload += " [Y] bridge has free space"
            else:
                payload += " [N] bridge has NOT free space"
                self.ask_freespace_to_other(remote_client_id)
            self.client.publish(topic, payload)
            logging.info(logging_msg + payload)
        elif command == 'BOOK':
            title = msg_list[2]
            if self.locker.check_book_from_title(title):
                payload += " [Y] bridge has the book"
            else:
                payload += " [N] bridge has NOT the book"
                self.ask_book_to_other(remote_client_id, title)
            self.client.publish(topic, payload)
            logging.info(logging_msg + payload)
        elif command == 'RESERVE':
            title = msg_list[2]
            if self.locker.reserve_book_from_title(remote_client_id, title):
                payload += " [Y] bridge has reserved the book"
            else:
                payload += " [N] bridge has NOT reserved the book"
            self.client.publish(topic, payload)
            logging.info(logging_msg + payload)
        else:
            payload += 'NOT DONE'
            self.client.publish(topic, payload)
            logging.info(logging_msg + payload)

    # function activated by the client
    def on_bridges_query(self, client_id, userdata, msg):
        client_id = msg.payload.decode()
        logging.info('[bridges query] ' + msg.topic + " " + str(msg.payload))
        topic = f'world/{self.state}/{self.region}/clients/{client_id}'
        payload = self.bridge_id
        payload += " is a bridge that can be achieved"
        self.client.publish(topic, payload)
        logging_msg = f'[on_bridges_query (client: {client_id}) mqtt msg PUBLISHED:{payload}]'
        logging.info(logging_msg)

    def on_book_query(self, client_id, userdata, msg):
        logging.info('[book query] ' + msg.topic + " " + str(msg.payload))
        msg_list = msg.payload.decode().split()
        client_id = msg_list[0]
        title = msg_list[1]

        # check if book is inside database
        topic = f'world/{self.state}/{self.region}/clients/{client_id}'
        payload = self.bridge_id
        if self.locker.check_book_from_title(title):
            payload += " [Y] bridge has the book"
        else:
            payload += " [N] bridge has NOT the book"
        self.client.publish(topic, payload)
        logging_msg = f'[on_book_query (bridge: {client_id}) mqtt msg PUBLISHED:{payload}]'
        logging.info(logging_msg)

    def on_freespace_query(self, client_id, userdata, msg):
        logging.info('[freespace query] ' + msg.topic + " " + str(msg.payload))
        msg_list = msg.payload.decode().split()
        client_id = msg_list[0]

        payload = self.bridge_id
        topic = f'world/{self.state}/{self.region}/clients/{client_id}'
        if self.locker.check_free_space():
            payload += " [Y] bridge has free space"
        else:
            payload += " [N] bridge has NOT free space"
        self.client.publish(topic, payload)
        logging_msg = f'[on_freespace_query (bridge: {client_id}) mqtt msg PUBLISHED:{payload}]'
        logging.info(logging_msg)

    '''def on_client_query(self, client_id, userdata, msg):
        logging.info('[client query] ' + msg.topic + " " + str(msg.payload))
        msg_list = msg.payload.decode().split()
        client_id = msg_list[0]

        payload = self.bridge_id
        topic = f'world/{self.state}/{self.region}/clients/{client_id}'
        if self.locker.get_client(client_id):
            payload += " is a bridge that can be achieved"
            self.client.publish(topic, payload)
        else:
            payload = "None"
        logging_msg = f'[on_client_query (bridge: {self.bridge_id}) mqtt msg PUBLISHED:{payload}]'
        logging.info(logging_msg)'''
