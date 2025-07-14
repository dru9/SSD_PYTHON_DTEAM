from enum import Enum
from dataclasses import dataclass


class Command(Enum):
    WRITE = "write"
    READ = "read"
    FULLWRITE = "fullwrite"
    FULLREAD = "fullread"
    HELP = "help"
    EXIT = "exit"
    SCRIPT_1 = "1_"
    SCRIPT_2 = "2_"
    SCRIPT_3 = "3_"
    INVALID = "invalid"


@dataclass
class Config:
    pass


class Shell:
    def __init__(self, config):
        self.config = config

    def execute_command(self, command, args):
        print("command executed")

    def get_command(self):
        try:
            user_input = input("Shell> ").strip()
            if not user_input:
                return None, []

            parts = user_input.split()
            command_str = parts[0]
            args = parts[1:]

            command = self.find_command(command_str)
            return command, args

        except (KeyboardInterrupt, EOFError):
            return Command.EXIT, []

    def read(self, lba: int):
        pass

    def write(self, lba: int, value: str):
        pass

    def write_error_to_output(self):
        pass

    def full_write(self, value: str):
        pass

    def full_read(self):
        pass

    def find_command(self, command_str: str):
        return 'c', 'a'

    def script_1(self):
        pass

    def script_2(self):
        pass

    def script_3(self):
        pass

    def main_loop(self):
        while True:
            command, args = self.get_command()

            if command is None:  # 빈 입력
                continue

            if command == 'c':
                print("command entered!")
                break

            self.execute_command(command, args)


if __name__ == "__main__":
    config = Config()
    shell = Shell(config)
    shell.main_loop()
