# -*- coding: utf-8 -*-
import zmq
import threading
import logging
from abc import ABC, abstractmethod


class BaseZMQListener(ABC):
    """
    A base class for ZMQ listener functionality.
    Derived classes should handle specific types of payloads.
    """

    LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"  # Log format

    def __init__(self, address: str, loglevel: int = logging.INFO):
        """
        Initialize the ZMQ listener.
        :param address: ZMQ listen address
        :param loglevel: Logging level
        """
        self.address = address
        self.context = zmq.Context()
        self.socket = self._initialize_socket()
        self.logger = self._setup_logger(loglevel)

    def __del__(self):
        if self.socket:
            self.socket.close()
        if self.context:
            self.context.term()

    def _setup_logger(self, loglevel: int) -> logging.Logger:
        """
        Set up and return a logger instance.
        :param loglevel: Logging level
        """
        logging.basicConfig(level=loglevel, format=self.LOG_FORMAT)
        return logging.getLogger(self.__class__.__name__)

    def _initialize_socket(self) -> zmq.Socket:
        """
        Set up and return a ZMQ subscription socket.
        """
        socket = self.context.socket(zmq.SUB)
        socket.connect(self.address)
        socket.setsockopt_string(zmq.SUBSCRIBE, "")
        return socket

    def start(self):
        """
        Start the ZMQ listener in a separate thread.
        """
        self.logger.info(f"ZMQ Client started at {self.address}")
        threading.Thread(target=self._listen_for_messages, daemon=True).start()

    def _listen_for_messages(self):
        """
        Main loop to listen for messages and handle them.
        """
        while True:
            try:
                message = self.socket.recv_json()
                self.logger.info(f"Received message: {message}")
                self.process(message)
            except Exception as error:
                self.logger.error(f"Error handling message: {error}")

    @abstractmethod
    def process(self, message: dict):
        """
        Process the incoming message.
        Must be implemented by subclasses.
        :param message: Incoming message (JSON payload)
        """
        pass
