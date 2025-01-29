import argparse
from enum import Enum

import numpy as np

from audio import register_output_callback
from base import NetMicBase
from communication import Message, ControlMessage, CommunicationException
from config import ClientConfig
from keyboard import listen, keyboard
import threading


class NetMicMode(Enum):
    CONSTANT = 0
    PUSH_TO_TALK = 1


def map_mode(mode: int) -> NetMicMode:
    switch = {
        0: NetMicMode.CONSTANT,
        1: NetMicMode.PUSH_TO_TALK,
    }
    return switch[mode]


def parse_args():
    parser = argparse.ArgumentParser("NetMic Server", formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("mode", help="0 - Constant\n1 - Push-To-Talk", type=int, default=0, nargs="?")
    return parser.parse_args()



class NetMicClient(NetMicBase):
    def __init__(self, config: ClientConfig, port: int, remote_port: int):
        super().__init__(port, remote_port, False)
        self.mode: NetMicMode = map_mode(config.mode)
        self.device_id: int = config.device_id
        self.server_ip: str = config.server_ip

    def init_transfer(self):
        self.channel_as_client.send(Message.control_message(ControlMessage.START))

        ack = self.channel_as_client.receive_response()
        if ack.control != ControlMessage.ACK:
            raise CommunicationException("START was not acknowledged")

        self.channel_as_server.open()

        self.channel_as_client.send(Message.control_message(ControlMessage.ACK))

        self.channel_as_server.listen()

        def callback(output: np.ndarray, *_):
            data = self.channel_as_server.receive().data
            output[:] = data

        register_output_callback(self.device_id, callback)

    def stop_transfer(self):
        self.channel_as_client.send(Message.control_message(ControlMessage.STOP))

        ack = self.channel_as_client.receive_response().control
        if ack != ControlMessage.ACK:
            raise CommunicationException("STOP was not acknowledged")

        self.channel_as_server.close()

    def on_press(self, key: keyboard.Key):
        try:
            if key.char == "t":
                threading.Thread(target=self.init_transfer).start()
        except AttributeError:
            pass

    def on_release(self, key: keyboard.Key):
        try:
            if key.char == "t":
                self.stop_transfer()
        except AttributeError:
            pass

    def run(self):
        self.channel_as_client.open(self.server_ip)

        # TODO add transfer running flag

        if self.mode == NetMicMode.CONSTANT:
            self.init_transfer()

        if self.mode == NetMicMode.PUSH_TO_TALK:
            listen(self.on_press, self.on_release)


if __name__ == '__main__':
    client = NetMicClient(ClientConfig(), 7777,7778)
    client.run()