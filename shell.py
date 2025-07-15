from dataclasses import dataclass

from commands import ReadCommand
from commands import WriteCommand
from consts.commands import CommandEnum
from consts.commands import VALUE_REQUIRE_COMMANDS
from consts.help_msg import HELP_MSG


@dataclass
class ShellConfig:
    SSD_PY_PATH = "ssd.py"
    OUTPUT_FILE_PATH = "ssd_output.txt"


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

    def _read_output_file(self) -> str:
        try:
            with open(self.config.OUTPUT_FILE_PATH, 'r') as f:
                content = f.read().strip()
                return content
        except FileNotFoundError:
            return "ERROR"
        except Exception:
            return "ERROR"

    def _read_core(self, lba: int) -> str:
        command = ReadCommand(self.config.SSD_PY_PATH, lba)
        subprocess_success = command.execute()

        if not subprocess_success:
            return "ERROR"

        return self._read_output_file()

    def read(self, lba: int) -> str:
        lba = int(lba)  # todo: safe convert
        result = self._read_core(lba)
        if result == "ERROR":
            return "[Read] ERROR"
        else:
            return f"[Read] LBA {lba:02d} : {result}"

    def _write_core(self, lba: int, value: str) -> bool:
        command = WriteCommand(self.config.SSD_PY_PATH, lba, value)
        subprocess_success = command.execute()

        if not subprocess_success:
            return False

        result = self._read_output_file()
        if result == "":
            return True
        else:
            return False

    def write(self, lba: int, value: str) -> str:
        success = self._write_core(lba, value)
        return "[Write] Done" if success else "[Write] ERROR"

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
        if command == CommandEnum.HELP:
            print(HELP_MSG)
            return None
        elif command == CommandEnum.READ:
            return self.read(*args)
        elif command == CommandEnum.WRITE:
            return self.write(*args)
        elif command == CommandEnum.FULLREAD:
            return self.full_read()
        elif command == CommandEnum.FULLWRITE:
            return self.full_write(*args)
        elif command == CommandEnum.SCRIPT_1:
            return self.script_1()
        elif command == CommandEnum.SCRIPT_2:
            return self.script_2()
        elif command == CommandEnum.SCRIPT_3:
            return self.script_3()
        else:
            raise NotImplementedError()

    def main_loop(self):
        while True:
            command, args = self.get_command()

            if command is None:
                continue

            if command == CommandEnum.EXIT: break

            print(self.execute_command(command, args))


if __name__ == "__main__":
    config = ShellConfig()
    shell = Shell(config)
    shell.main_loop()
