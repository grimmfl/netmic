import json
import os
from collections.abc import Callable
from typing import List

from audio import query_devices

CLIENT_CONFIG_FILE = "client_config.json"
SERVER_CONFIG_FILE = "server_config.json"


class ConfigBase:
    def __init__(self, config_file: str, prompts: List[Callable]) -> None:
        self.config_file: str = config_file
        self.device_id: int = 0

        if self.try_load_config():
            return

        self.prompt_device_id()

        for prompt in prompts:
            prompt()

        self.prompt_save()

    def to_json(self):
        return json.dumps(
            self,
            default=lambda o: {k: v for k,v in o.__dict__.items() if k != "config_file"},
            sort_keys=True,
            indent=4
        )

    def from_json(self, content: str):
        data = json.loads(content)
        self.device_id = int(data["device_id"])

    def try_load_config(self) -> bool:
        cwd = os.getcwd()
        if self.config_file not in os.listdir(cwd):
            return False

        with open(self.config_file, "r", encoding="utf-8") as f:
            self.from_json(f.read())

        return True

    def prompt_device_id(self):
        print("Please enter a device id:")
        print(query_devices())
        self.device_id = int(input())

    def prompt_save(self):
        print("Do you want to save this configuration? (y/n)")
        response = input()
        if response.lower() == "y":
            with open(self.config_file, "w", encoding="utf-8") as f:
                f.write(self.to_json())


class ClientConfig(ConfigBase):
    def __init__(self):
        self.mode: int = 0
        self.server_ip: str = ""

        prompts = [
            self.prompt_server_ip,
            self.prompt_mode
        ]

        super().__init__(CLIENT_CONFIG_FILE, prompts)

    def prompt_mode(self):
        print("Which mode would you like to use?")
        print("\t 0 - Constant")
        print("\t 1 - Push-to-Talk")
        self.mode = int(input())

    def prompt_server_ip(self):
        print("Please enter the ip address of the server:")
        self.server_ip = input()

    def from_json(self, content: str):
        data = json.loads(content)
        self.device_id = int(data["device_id"])
        self.mode = int(data["mode"])
        self.server_ip = data["server_ip"]


class ServerConfig(ConfigBase):
    def __init__(self):
        super().__init__(SERVER_CONFIG_FILE, [])


if __name__ == '__main__':
    config = ServerConfig()
