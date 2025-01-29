from communication import CommunicationClient, CommunicationServer, CONTROL_MESSAGE_SIZE, DATA_MESSAGE_SIZE


class NetMicBase:
    def __init__(self, port: int, remote_port: int, is_server: bool):
        self.channel_as_client = CommunicationClient(remote_port, message_size=DATA_MESSAGE_SIZE if is_server else CONTROL_MESSAGE_SIZE)
        self.channel_as_server = CommunicationServer(port, message_size=CONTROL_MESSAGE_SIZE if is_server else DATA_MESSAGE_SIZE)

    def run(self):
        pass
