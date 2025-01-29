import numpy as np

from audio import register_input_callback
from base import NetMicBase
from communication import Message, ControlMessage, CommunicationException
from config import ServerConfig


class NetMicServer(NetMicBase):
    def __init__(self, config: ServerConfig, port: int, remote_host: str, remote_port: int):
        super().__init__(port, remote_host, remote_port, True)
        self.device_id = config.device_id

    def run(self):
        def callback(data: np.ndarray, *_):
            self.channel_as_client.send(Message.data_message(data))

        self.channel_as_server.open()
        self.channel_as_server.listen()
        message = self.channel_as_server.receive()

        if message.control != ControlMessage.START:
            raise CommunicationException("Expected START")

        self.channel_as_server.respond(Message.control_message(ControlMessage.ACK))

        ack = self.channel_as_server.receive().control
        if ack != ControlMessage.ACK:
            raise CommunicationException("ACK was not acknowledged")

        self.channel_as_client.open()

        register_input_callback(self.device_id, callback)


if __name__ == '__main__':
    server = NetMicServer(ServerConfig(), 7778, "127.0.0.1", 7777)
    server.run()