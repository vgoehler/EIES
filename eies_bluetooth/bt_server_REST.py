#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import signal
import sys
import configparser

from flask import Flask, request, jsonify
import bluetooth


class BluetoothServer(object):
    def __init__(self):
        # These get read in by the configuration
        self.host = None
        self.server_port = None
        self.server_uuid = None
        self.server_name = "Not Set"
        # These we need for the connection
        self.server_sock = None
        self.client_sock = None

        # Initialize logger
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s - %(levelname)s - %(message)s',
        )
        self.logger = logging.getLogger("BluetoothServer")

        self.read_config()

        # Handle termination signals
        signal.signal(signal.SIGINT, self.terminate)
        signal.signal(signal.SIGTERM, self.terminate)

        # Initialize Flask app
        self.app = Flask(__name__)
        self.app.add_url_rule('/control', 'control', self.control, methods=['POST'])

    def read_config(self):
        """
        Load configuration settings from serverconfig.ini.
        """
        config = configparser.ConfigParser()
        config.read('serverconfig.ini')

        self.host = config["Server"]["host"]
        self.server_port = int(config["Server"]["port"])
        self.server_uuid = config["Connect"]["uuid"]
        self.server_name = config["Connect"]["name"]

        self.logger.info("Configuration loaded successfully")

    def send_data(self, data):
        """
        Send data over Bluetooth serial connection.
        """
        try:
            self.logger.info(f"Sending data: {data}")
            self.client_sock.sendall(data.encode('utf-8'))
        except bluetooth.BluetoothError as e:
            self.logger.error(f"BluetoothError: {e}")

    def control(self):
        """
        REST endpoint to receive control data and send over Bluetooth.
        Expected JSON format: { "LED": "some_data" }
        """
        try:
            data = request.get_json()
            if "LED" in data:
                self.send_data(data["LED"])
                return jsonify({"status": "success", "message": "Data sent"}), 200
            else:
                return jsonify({"status": "error", "message": "Invalid input"}), 400
        except Exception as e:
            self.logger.exception("Error handling request")
            return jsonify({"status": "error", "message": str(e)}), 500

    def run(self):
        """
        Start the Flask server using configuration settings.
        """
        self.logger.info("Starting Bluetooth server")
        self.connect_bt()
        self.logger.info(f"Starting REST server on {self.host}:{self.server_port}")
        # deactivate reloader as this opens a second BT connection
        self.app.run(host=self.host, port=self.server_port, debug=True, use_reloader=False)

    def terminate(self, signum, frame):
        """
        Handle termination signals.
        """
        self.logger.info("Termination signal received. Shutting down...")
        # closing of connection is handled by destructor
        sys.exit(0)

    def connect_bt(self):
        self.server_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        self.server_sock.bind(("", bluetooth.PORT_ANY))
        self.server_sock.listen(1) # advertise needs a listen on the socket else bluetooth error
        port = self.server_sock.getsockname()[1]

        bluetooth.advertise_service(self.server_sock, self.server_name, service_id=self.server_uuid,
                                    service_classes=[self.server_uuid, bluetooth.SERIAL_PORT_CLASS],
                                    profiles=[bluetooth.SERIAL_PORT_PROFILE]
                                    )
        self.logger.info(f"Waiting for connection on RFCOMM channel {port}")

        self.client_sock, client_info = self.server_sock.accept()
        self.logger.info(f"Accepted connection from {client_info}")

def __del__(self):
    if self.client_sock:
        self.logger.info("closing client connection")
        self.client_sock.close()
    if self.server_sock:
        self.logger.info("closing server")
        self.server_sock.close()

if __name__ == '__main__':
    bt_server = BluetoothServer()
    bt_server.run()
