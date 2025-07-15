from __future__ import annotations

from typing import Optional

import utils
from commands import ReadShellCommand, WriteShellCommand
from constant import (
    FILENAME_MAIN_SSD,
    FILENAME_OUT,
    MESSAGE_DONE,
    MESSAGE_ERROR,
    MESSAGE_FAIL,
    MESSAGE_HELP,
    MESSAGE_INVALID_SHELL_CMD,
    MESSAGE_PASS,
    ShellCommandEnum
)

TWO_ARGS_REQUIRE_COMMANDS = [ShellCommandEnum.WRITE]
ONE_ARGS_REQUIRE_COMMANDS = [ShellCommandEnum.READ, ShellCommandEnum.FULLWRITE]


class SSDReaderWriter:

    @classmethod
    def read(cls, lba: int) -> str:
        cmd = ReadShellCommand(FILENAME_MAIN_SSD, lba)
        is_ssd_run = cmd.execute()
        if not is_ssd_run:
            return MESSAGE_ERROR

        return cls._cache_inout()

    @classmethod
    def write(cls, lba: int, value: str) -> str:
        cmd = WriteShellCommand(FILENAME_MAIN_SSD, lba, value)
        is_ssd_run = cmd.execute()
        if not is_ssd_run:
            return MESSAGE_ERROR

        res = cls._cache_inout()
        if res == "":
            return MESSAGE_DONE

        return MESSAGE_ERROR

    @classmethod
    def _cache_inout(cls) -> str:
        try:
            with open(FILENAME_OUT, "r") as f:
                content = f.read().strip()
                return content

        except FileNotFoundError:
            return MESSAGE_ERROR

        except Exception:
            return MESSAGE_ERROR


class ShellParser:

    @classmethod
    def parse(cls):
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


class Shell:
    reader_writer = SSDReaderWriter
    shell_parser = ShellParser
    _command_mapping_dict = None

    @classmethod
    def _command_mapper(cls, cmd):
        if cls._command_mapping_dict is None:
            cls._command_mapping_dict = {
                ShellCommandEnum.HELP: lambda: print(MESSAGE_HELP),
                ShellCommandEnum.READ: cls.read,
                ShellCommandEnum.WRITE: cls.write,
                ShellCommandEnum.FULLREAD: cls.full_read,
                ShellCommandEnum.FULLWRITE: cls.full_write,
                ShellCommandEnum.SCRIPT_1: cls.script_1,
                ShellCommandEnum.SCRIPT_2: cls.script_2,
                ShellCommandEnum.SCRIPT_3: cls.script_3,
                ShellCommandEnum.INVALID: lambda: print(MESSAGE_INVALID_SHELL_CMD)
            }
        return cls._command_mapping_dict[cmd]

    @classmethod
    def read(cls, lba: int) -> str:
        lba = int(lba)  # todo: safe convert
        ret = cls.reader_writer.read(lba)
        if ret == MESSAGE_ERROR:
            return "[Read] ERROR"
        return f"[Read] LBA {lba:02d} : {ret}"

    @classmethod
    def write(cls, lba: int, value: str) -> str:
        ret = cls.reader_writer.write(lba, value)
        if ret == MESSAGE_ERROR:
            return "[Write] ERROR"
        return "[Write] Done"

    @classmethod
    def full_write(cls, value: str):
        for lba in range(100):
            ret = cls.reader_writer.write(lba, value)
            if ret == MESSAGE_ERROR:
                return f"[Full Write] ERROR in LBA[{lba:02d}]"
        return "[Full Write] Done"

    @classmethod
    def full_read(cls, num_iter: int = 100) -> str:
        header = "[Full Read]"
        results = [header]
        results += [
            f"LBA {i:0>2} : {cls.reader_writer.read(lba=i)}"
            for i in range(num_iter)
        ]
        return "\n".join(results)

    @classmethod
    def script_1(cls, num_iter: int = 20) -> str:
        for n in range(num_iter):
            start_idx = n * 5
            value = utils.get_random_value()
            for i in range(5):
                if not cls.reader_writer.write(lba=start_idx + i, value=value):
                    return MESSAGE_FAIL
            for i in range(5):
                if value != cls.reader_writer.read(lba=start_idx + i):
                    return MESSAGE_FAIL
        return MESSAGE_PASS

    @classmethod
    def script_2(cls, num_iter: int = 30) -> str:
        lba_values: list[int] = [4, 0, 3, 1, 2]
        for _ in range(num_iter):
            value = utils.get_random_value()
            for lba in lba_values:
                success = cls.reader_writer.write(lba, value)
                if not success:
                    return MESSAGE_FAIL

            for lba in lba_values:
                current_value = cls.reader_writer.read(lba)
                if current_value == MESSAGE_ERROR:
                    return MESSAGE_FAIL
                if current_value != value:
                    return MESSAGE_FAIL

        return MESSAGE_PASS

    @classmethod
    def script_3(cls, num_iter: int = 200) -> str:
        lba_1, lba_2 = (0, 99)
        for _ in range(num_iter):
            value = utils.get_random_value()
            cls.reader_writer.write(lba=lba_1, value=value)
            cls.reader_writer.write(lba=lba_2, value=value)
            if cls.reader_writer.read(lba_1) != cls.reader_writer.read(lba_2):
                return MESSAGE_FAIL
        return MESSAGE_PASS

    @classmethod
    def run(cls) -> None:
        while True:
            cmd, args = cls.shell_parser.parse()
            if cmd == ShellCommandEnum.EXIT:
                break

            ret = cls.execute_command(cmd, args)
            if ret is not None:
                print(ret)

    @classmethod
    def execute_command(cls, cmd: str, args: list) -> Optional[str]:
        func = cls._command_mapper(cmd)
        return func(*args)


if __name__ == "__main__":
    Shell.run()
