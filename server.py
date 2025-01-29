import numpy as np

from audio import register_input_callback
from base import NetMicBase
from communication import Message, ControlMessage, CommunicationException
from config import ServerConfig
import threading


class NetMicServer(NetMicBase):
    def __init__(self, config: ServerConfig, port: int, remote_port: int):
        super().__init__(config.my_ip, port, remote_port, True)
        self.device_id = config.device_id

    def stop_transfer(self):
        self.channel_as_client.close()
        self.channel_as_server.respond(Message.control_message(ControlMessage.ACK))

    def listen_for_controls(self):
        message = self.channel_as_server.receive().control
        print(message)
        if message == ControlMessage.STOP:
            self.stop_transfer()

    def run(self):
        def callback(data: np.ndarray, *_):
            self.channel_as_client.send(Message.data_message(data))
            del data

        self.channel_as_server.open()
        address = self.channel_as_server.listen()
        message = self.channel_as_server.receive()

        if message.control != ControlMessage.START:
            raise CommunicationException("Expected START")

        self.channel_as_server.respond(Message.control_message(ControlMessage.ACK))

        ack = self.channel_as_server.receive().control
        if ack != ControlMessage.ACK:
            raise CommunicationException("ACK was not acknowledged")

        self.channel_as_client.open(address)

        threading.Thread(target=register_input_callback, args=[self.device_id, callback]).start()
        threading.Thread(target=self.listen_for_controls).start()

        # TODO stop threads


if __name__ == '__main__':
    server = NetMicServer(ServerConfig(), 7778, 7777)
    server.run()