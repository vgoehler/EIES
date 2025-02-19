#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import configparser
import logging
import signal
from abc import abstractmethod

import bluetooth


class Listener(object):

    def __init__(self, loglevel=logging.DEBUG):
        self.server_uuid = None
        self.server_name = None

        # Initialize logger
        logging.basicConfig(
            level=loglevel,
            format='%(asctime)s - %(levelname)s - %(message)s',
        )
        self.logger = logging.getLogger("BluetoothListener")

        self.read_config('config.ini')

        # Handle termination signals
        signal.signal(signal.SIGINT, self.terminate)
        signal.signal(signal.SIGTERM, self.terminate)

    @abstractmethod
    def payload(self, data):
        """
        do something after you got a message
        :data: the data to do something with
        :return:
        """
        self.logger.debug(f"Received data: {data}")

    @abstractmethod
    def payload_setup(self):
        pass

    def listen(self):
        """
        listen on the connection
        :return:
        """
        try:
            search_server = bluetooth.find_service(uuid=self.server_uuid, name=self.server_name)

            if len(search_server) == 0:
                self.logger.info(f"Couldn't find bluetooth server {self.server_name}")
                sys.exit(0)
            elif len(search_server) > 1:
                self.logger.error(f"Found more than one bluetooth server {search_server}")
                sys.exit(1)

            port = search_server[0]['port']
            name = search_server[0]['name']
            host = search_server[0]['host']

            self.logger.info(f"Listening on {port}:{name}:{host}")

            self.payload_setup()

            sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
            sock.connect((host, port))
            self.logger.info("BT Connected. Listening ...")


            while True:
                data = sock.recv(1024)
                if data:
                    self.logger.info(f"Data received: {data}")
                    self.payload(data)
        except bluetooth.BluetoothError as e:
            self.logger.error(f"Bluetooth connection error: {e}")
        except Exception as e:
            self.logger.exception(f"Unexpected error: {e}")

    def read_config(self, cfg: str):
        """

        :return:
        """
        # Load Configuration
        config = configparser.ConfigParser()
        config.read(cfg)

        self.server_uuid = config["Connect"]["uuid"]
        self.server_name = config["Connect"]["name"]

        self.logger.info("Configuration loaded successfully")

    def terminate(self, signum, frame):
        """
        Handle termination signals.
        """
        self.logger.info("Termination signal received. Shutting down...")
        sys.exit(0)



if __name__ == "__main__":
    listener = Listener()
    listener.listen()
