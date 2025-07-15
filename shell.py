from typing import Optional

import utils
from commands import ReadShellCommand, WriteShellCommand
from constant import (FILENAME_MAIN_SSD, FILENAME_OUT, HELP_MSG, ShellCommandEnum)

TWO_ARGS_REQUIRE_COMMANDS = [ShellCommandEnum.WRITE]
ONE_ARGS_REQUIRE_COMMANDS = [ShellCommandEnum.READ, ShellCommandEnum.FULLWRITE]


class Shell:

    @classmethod
    def get_command(cls):
        try:
            user_input = input("Shell> ").strip()
            if not user_input:
                return None, []

            parts = user_input.split()
            cmd_str = parts[0]
            args = parts[1:]
            cmd = cls.find_command(cmd_str)

            if cmd in TWO_ARGS_REQUIRE_COMMANDS and len(args) != 2:
                return ShellCommandEnum.INVALID, []

            if cmd in ONE_ARGS_REQUIRE_COMMANDS and len(args) != 1:
                return ShellCommandEnum.INVALID, []

            return cmd, args

        except (KeyboardInterrupt, EOFError):
            return ShellCommandEnum.EXIT, []

    @classmethod
    def find_command(cls, command_str: str):
        command_str = command_str.lower()
        for cmd in ShellCommandEnum:
            if cmd.value == command_str:
                return cmd
            elif cmd.value.lower().startswith(command_str):
                return cmd

        return ShellCommandEnum.INVALID

    @classmethod
    def _read_output_file(cls) -> str:
        try:
            with open(FILENAME_OUT, "r") as f:
                content = f.read().strip()
                return content
        except FileNotFoundError:
            return "ERROR"
        except Exception:
            return "ERROR"

    @classmethod
    def _read_value(cls, lba: int) -> str:
        command = ReadShellCommand(FILENAME_MAIN_SSD, lba)
        subprocess_success = command.execute()
        if not subprocess_success:
            return "ERROR"

        return cls._read_output_file()

    @classmethod
    def read(cls, lba: int) -> str:
        lba = int(lba)  # todo: safe convert
        result = cls._read_value(lba)
        if result == "ERROR":
            return "[Read] ERROR"
        else:
            return f"[Read] LBA {lba:02d} : {result}"

    @classmethod
    def _write_value(cls, lba: int, value: str) -> bool:
        command = WriteShellCommand(FILENAME_MAIN_SSD, lba, value)
        subprocess_success = command.execute()
        if not subprocess_success:
            return False

        result = cls._read_output_file()
        if result == "":
            return True
        else:
            return False

    @classmethod
    def write(cls, lba: int, value: str) -> str:
        success = cls._write_value(lba, value)
        return "[Write] Done" if success else "[Write] ERROR"

    @classmethod
    def full_write(cls, value: str):
        for i in range(100):
            ret = cls.write(i, value)
            if ret == "[Write] ERROR":
                return f"[Full Write] ERROR in LBA[{i:02d}]"
        return "[Full Write] Done"

    @classmethod
    def full_read(cls, num_iter: int = 100) -> str:
        header = "[Full Read]"
        results = [header]
        results += [
            f"LBA {i:0>2} : {cls._read_value(lba=i)}"
            for i in range(num_iter)
        ]
        return "\n".join(results)

    @classmethod
    def script_1(cls, num_iter: int = 20) -> str:
        for n in range(num_iter):
            start_idx = n * 5
            value = utils.get_random_value()
            for i in range(5):
                if not cls._write_value(lba=start_idx + i, value=value):
                    return "FAIL"
            for i in range(5):
                if value != cls._read_value(lba=start_idx + i):
                    return "FAIL"
        return "PASS"

    @classmethod
    def script_2(cls, num_iter: int = 30) -> str:
        lba_values: list[int] = [4, 0, 3, 1, 2]
        for _ in range(num_iter):
            value = utils.get_random_value()
            for lba in lba_values:
                success = cls._write_value(lba, value)
                if not success:
                    return "FAIL"

            for lba in lba_values:
                current_value = cls._read_value(lba)
                if current_value == "ERROR":
                    return "FAIL"
                if current_value != value:
                    return "FAIL"

        return "PASS"

    @classmethod
    def script_3(cls, num_iter: int = 200) -> str:
        lba_1, lba_2 = (0, 99)
        for _ in range(num_iter):
            value = utils.get_random_value()
            cls._write_value(lba=lba_1, value=value)
            cls._write_value(lba=lba_2, value=value)
            if cls._read_value(lba_1) != cls._read_value(lba_2):
                return "FAIL"
        return "PASS"

    @classmethod
    def execute_command(cls, cmd: str, args: list) -> Optional[str]:
        print(f"Entered command: {cmd}  with args: {args}")
        if cmd == ShellCommandEnum.HELP:
            print(HELP_MSG)
            return None
        elif cmd == ShellCommandEnum.READ:
            return cls.read(*args)
        elif cmd == ShellCommandEnum.WRITE:
            return cls.write(*args)
        elif cmd == ShellCommandEnum.FULLREAD:
            return cls.full_read()
        elif cmd == ShellCommandEnum.FULLWRITE:
            return cls.full_write(*args)
        elif cmd == ShellCommandEnum.SCRIPT_1:
            return cls.script_1()
        elif cmd == ShellCommandEnum.SCRIPT_2:
            return cls.script_2()
        elif cmd == ShellCommandEnum.SCRIPT_3:
            return cls.script_3()
        else:
            raise NotImplementedError(f"Not implemented function for '{cmd}'")

    @classmethod
    def run(cls) -> None:
        while True:
            cmd, args = cls.get_command()
            if cmd == ShellCommandEnum.EXIT:
                break
            if cmd is None:
                continue
            print(cls.execute_command(cmd, args))


if __name__ == "__main__":
    Shell.run()
