import random

from dataclasses import dataclass

from commands import ReadCommand, WriteCommand
from constant import CommandEnum


VALUE_REQUIRE_COMMANDS = [CommandEnum.WRITE, CommandEnum.FULLWRITE]


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
        for i in range(100):
            ret = self.write(i, value)
            if ret == "[Write] ERROR":
                return f"[Full Write] ERROR in LBA[{i:02d}]"
        return "[Full Write] Done"

    def full_read(self, num_iter: int = 100) -> str:
        header = "[Full Read]"
        results = [header]
        results += [
            f"LBA {i:0>2} : {self._read_core(lba=i)}"
            for i in range(num_iter)
        ]
        return "\n".join(results)

    def script_1(self) -> str:
        for num_iter in range(20):
            start_idx = num_iter * 5
            value = str(random.randint(0, 99_999_999)).zfill(8)
            for i in range(5):
                if not self._write_core(lba=start_idx + i, value=value):
                    return "FAIL"
            for i in range(5):
                if value != self._read_core(lba=start_idx + i):
                    return "FAIL"
        return "PASS"

    def script_2(self):
        REPEAT_TIMES = 30
        LBAS = [4, 0, 3, 1, 2]
        RAND_LOWER_BOUND = 0
        RAND_UPPER_BOUND = 0xFFFFFFFF
        for iteration in range(REPEAT_TIMES):
            writing_random_value = f"0x{random.randint(RAND_LOWER_BOUND, RAND_UPPER_BOUND):08X}"

            for lba in LBAS:
                success = self._write_core(lba, writing_random_value)
                if not success:
                    return f"FAIL - Write error at {lba} in iter: {iteration + 1}"

            for lba in LBAS:
                current_value = self._read_core(lba)
                if current_value == "ERROR":
                    return f"FAIL - Read error at {lba} in iter: {iteration + 1}"
                if current_value != writing_random_value:
                    return f"FAIL - Value mismatch at {lba} in iter: {iteration + 1}"

        return "PASS"

    def script_3(self, num_iter: int = 200) -> None:
        lba_1, lba_2 = (0, 99)
        for _ in range(num_iter):
            value = str(random.randint(0, 99_999_999)).zfill(8)
            self._write_core(lba=lba_1, value=value)
            self._write_core(lba=lba_2, value=value)
            assert self._read_core(lba_1) == self._read_core(lba_2), "Invalid results from test script 3"

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
