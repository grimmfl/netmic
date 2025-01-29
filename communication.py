import socket
import pickle
from typing import Any
from enum import Enum
import time

import numpy as np

DELIMITER = "#"
CONTROL_MESSAGE_SIZE = 93
DATA_MESSAGE_SIZE = 2281


class CommunicationException(Exception):
    def __init__(self, message: str):
        super().__init__(message)


class ControlMessage(Enum):
    NONE = 0
    START = 1
    STOP = 2
    ACK = 3


class Message:
    def __init__(self, control: ControlMessage, data: Any):
        self.control = control
        self.data = data

    def encode(self) -> bytes:
        return pickle.dumps(self)

    @staticmethod
    def decode(data: bytes) -> "Message":
        try:
            return pickle.loads(data)
        except pickle.UnpicklingError:
            return Message(ControlMessage.NONE, np.zeros((512, 16)))
        except ValueError:
            return Message(ControlMessage.NONE, np.zeros((512, 16)))

    @staticmethod
    def data_message(data: Any) -> "Message":
        return Message(ControlMessage.NONE, data)

    @staticmethod
    def control_message(control: ControlMessage) -> "Message":
        return Message(control, None)

    @property
    def is_control(self) -> bool:
        return self.control != ControlMessage.NONE


class CommunicationClient:
    def __init__(self, remote_port: int, message_size: int):
        self.remote_port: int = remote_port
        self.message_size: int = message_size
        self.socket = None

    def open(self, host: str):
        while True:
            try:
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.socket.connect((host, self.remote_port))
                return
            except ConnectionRefusedError:
                time.sleep(0.2)

    def close(self):
        self.socket.close()

    def send(self, message: Message):
        encoded = message.encode()
        self.socket.sendall(encoded)

    def receive_response(self) -> Message:
        response = self.socket.recv(self.message_size)
        return Message.decode(response)


class CommunicationServer:
    def __init__(self, host: str, port: int, message_size: int):
        self.host: str = host
        self.port: int = port
        self.message_size: int = message_size
        self.socket = None
        self.conn = None

    def open(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((self.host, self.port))

    def listen(self) -> str:
        self.socket.listen()
        self.conn, addr = self.socket.accept()
        return addr[0]

    def close(self):
        self.conn.close()
        self.socket.close()

    def receive(self):
        data = self.conn.recv(self.message_size)
        if data is not None:
            return Message.decode(data)

    def respond(self, message: Any):
        encoded = message.encode()
        print(len(encoded))
        self.conn.sendall(encoded)

