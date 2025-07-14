from dataclasses import dataclass

from consts.commands import Command
from consts.commands import VALUE_REQUIRE_COMMANDS
from consts.help_msg import HELP_MSG


@dataclass
class ShellConfig:
    SSD_PY_PAHT = "ssd.py"


class Shell:
    def __init__(self, config: ShellConfig):
        self.config = config

    def get_command(self):
        try:
            user_input = input("Shell> ").strip()
            if not user_input:
                return None, []

            parts = user_input.split()
            cmd_str = parts[0]
            args = parts[1:]

            cmd = self.find_command(cmd_str)

            if cmd in VALUE_REQUIRE_COMMANDS and len(args) == 0:
                return Command.INVALID, []

            return cmd, args

        except (KeyboardInterrupt, EOFError):
            return Command.EXIT, []

    @staticmethod
    def find_command(command_str: str):
        command_str = command_str.lower()

        for cmd in Command:
            if cmd.value == command_str:
                return cmd
            elif cmd.value.startswith(command_str):
                return cmd

        return Command.INVALID

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

    def script_1(self):
        pass

    def script_2(self):
        pass

    def script_3(self):
        pass

    def execute_command(self, command: str, args: list):
        print(f"Entered command: {command}  with args: {args}")
        if command == Command.HELP:
            print(HELP_MSG)

    def main_loop(self):
        while True:
            command, args = self.get_command()

            if command is None:
                continue

            if command == Command.EXIT: break

            self.execute_command(command, args)


if __name__ == "__main__":
    config = ShellConfig()
    shell = Shell(config)
    shell.main_loop()
