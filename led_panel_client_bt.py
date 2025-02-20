#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
import zmq
from bt_client import Listener


class LedPanelClient(Listener):
    """
    Gets Data over Bluetooth and retransmits them via zmq (locally)
    """

    def __init__(self, loglevel=logging.DEBUG):
        super().__init__(loglevel=loglevel)
        self.zmq_socket = None

    def payload(self, data):
        super().payload(data)
        self.zmq_socket.send_string(data)

    def payload_setup(self):
        context = zmq.Context()
        self.zmq_socket = context.socket(zmq.PUB)
        self.zmq_socket.bind("tcp://127.0.0.1:5555")

        self.logger.info("ZMQ Server: established")

    def __del__(self):
        if self.zmq_socket:
            self.zmq_socket.close()