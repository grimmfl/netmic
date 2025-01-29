import argparse
from enum import Enum

import numpy as np

from audio import register_output_callback
from base import NetMicBase
from communication import Message, ControlMessage, CommunicationException
from config import ClientConfig


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
    def __init__(self, config: ClientConfig, port: int, remote_host: str, remote_port: int):
        super().__init__(port, remote_host, remote_port, False)
        self.mode: NetMicMode = map_mode(config.mode)
        self.device_id: int = config.device_id

    def run(self):
        self.channel_as_client.open()

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


if __name__ == '__main__':
    client = NetMicClient(ClientConfig(), 7777, "127.0.0.1", 7778)
    client.run()