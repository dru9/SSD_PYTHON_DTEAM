from dataclasses import dataclass

from consts.commands import CommandEnum
from consts.commands import VALUE_REQUIRE_COMMANDS
from consts.help_msg import HELP_MSG


@dataclass
class ShellConfig:
    SSD_PY_PATH = "ssd.py"


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
                return CommandEnum.INVALID, []

            return cmd, args

        except (KeyboardInterrupt, EOFError):
            return CommandEnum.EXIT, []

    @staticmethod
    def find_command(command_str: str):
        command_str = command_str.lower()

        for cmd in CommandEnum:
            if cmd.value == command_str:
                return cmd
            elif cmd.value.startswith(command_str):
                return cmd

        return CommandEnum.INVALID

    def read(self, lba: int):
        pass

    def write(self, lba: int, value: str):
        pass

    def write_error_to_output(self):
        pass

    def full_write(self, value: str):
        for i in range(100):
            ret = self.write(i, value)
            if ret == "[Write] ERROR":
                return f"[Full Write] ERROR in LBA[{i:02d}]"
        return "[Full Write] Done"

    def full_read(self) -> str:
        header = "[Full Read]"
        num_iter: int = 100
        results = [header]
        results += [
            f"LBA {i:0>2} : {self.read(lba=i)}"
            for i in range(num_iter)
        ]
        return "\n".join(results)

    def script_1(self):
        pass

    def script_2(self):
        pass

    def script_3(self):
        pass

    def execute_command(self, command: str, args: list):
        print(f"Entered command: {command}  with args: {args}")
        if command == CommandEnum.HELP:
            print(HELP_MSG)

    def main_loop(self):
        while True:
            command, args = self.get_command()

            if command is None:
                continue

            if command == CommandEnum.EXIT: break

            self.execute_command(command, args)


if __name__ == "__main__":
    config = ShellConfig()
    shell = Shell(config)
    shell.main_loop()
