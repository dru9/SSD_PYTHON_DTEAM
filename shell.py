from __future__ import annotations

import sys  # noqa
from typing import Callable, Optional

import utils
from commands import EraseShellCommand, FlushShellCommand, ReadShellCommand, WriteShellCommand
from constant import (
    FILENAME_MAIN_SSD,
    FILENAME_OUT,
    FILENAME_SCRIPT_DEFAULT,
    MESSAGE_DONE,
    MESSAGE_ERROR,
    MESSAGE_FAIL,
    MESSAGE_HELP,
    MESSAGE_INVALID_SHELL_CMD,
    MESSAGE_PASS,
    SIZE_LBA,
    ShellCommandEnum
)
from logger import Logger

TWO_ARGS_REQUIRE_COMMANDS = [ShellCommandEnum.WRITE]
ONE_ARGS_REQUIRE_COMMANDS = [
    ShellCommandEnum.READ,
    ShellCommandEnum.FULLWRITE,
    ShellCommandEnum.ERASE,
    ShellCommandEnum.ERASE_RANGE,
]


class SSDController:

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
    def erase(cls, lba: int, size: int) -> str:
        cmd = EraseShellCommand(FILENAME_MAIN_SSD, lba, size)
        is_ssd_run = cmd.execute()
        if not is_ssd_run:
            return MESSAGE_ERROR

        res = cls._cache_inout()
        if res == "":
            return MESSAGE_DONE

        return MESSAGE_ERROR

    @classmethod
    def flush(cls):
        cmd = FlushShellCommand(FILENAME_MAIN_SSD)
        is_ssd_run = cmd.execute()
        if not is_ssd_run:
            return MESSAGE_ERROR

        res = cls._cache_inout()
        if res == "":
            return MESSAGE_DONE

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


class CommandExecutor:
    ssd_controller = SSDController
    logging: Callable = Logger().print

    @classmethod
    def read(cls, lba: int) -> str:
        lba = int(lba)  # todo: safe convert
        ret = cls.ssd_controller.read(lba)
        if ret == MESSAGE_ERROR:
            return "[Read] ERROR"

        cls.logging("... COMPLETE")
        return f"[Read] LBA {lba:02d} : {ret}"

    @classmethod
    def write(cls, lba: int, value: str) -> str:
        ret = cls.ssd_controller.write(lba, value)
        if ret == MESSAGE_ERROR:
            return "[Write] ERROR"

        cls.logging("... COMPLETE")
        return "[Write] Done"

    @classmethod
    def full_write(cls, value: str):
        for lba in range(SIZE_LBA):
            ret = cls.ssd_controller.write(lba, value)
            if ret == MESSAGE_ERROR:
                return f"[Full Write] ERROR in LBA[{lba:02d}]"

        cls.logging("... COMPLETE")
        return "[Full Write] Done"

    @classmethod
    def full_read(cls, num_iter: int = SIZE_LBA) -> str:
        header = "[Full Read]"
        results = [header]
        results += [
            f"LBA {i:0>2} : {cls.ssd_controller.read(lba=i)}"
            for i in range(num_iter)
        ]
        cls.logging("... COMPLETE")
        return "\n".join(results)

    @classmethod
    def erase(cls, lba: int, size: int) -> str:
        if not utils.validate_erase_args(lba, size):
            return "[Erase] ERROR"

        step = 10
        start, end = (lba, lba + size)
        for i in range(start, end, step):
            _start, _end = (i, min(i + step, end))
            _size = _end - _start
            ret = cls.ssd_controller.erase(lba=_start, size=_size)
            if ret == MESSAGE_ERROR:
                return "[Erase] ERROR"

        cls.logging("... COMPLETE")
        return "[Erase] Done"

    @classmethod
    def erase_range(cls, start_lba: int, end_lba: int) -> str:
        if not utils.validate_erase_range_args(start_lba, end_lba):
            return "[Erase Range] ERROR"

        erasing_size = end_lba - start_lba + 1
        ret = cls.erase(start_lba, erasing_size)
        if MESSAGE_ERROR in ret:
            return "[Erase Range] ERROR"

        cls.logging("... COMPLETE")
        return "[Erase Range] Done"

    @classmethod
    def flush(cls):
        ret = cls.ssd_controller.flush()
        if ret == MESSAGE_ERROR:
            return "[Flush] ERROR"

        cls.logging("... COMPLETE")
        return "[Flush] Done"


class ScriptExecutor:
    ssd_controller = SSDController
    command_executor = CommandExecutor
    logging: Callable = Logger().print

    @classmethod
    def script_1(cls, num_iter: int = 20) -> str:
        for n in range(num_iter):
            start_idx = n * 5
            value = utils.get_random_value()
            for i in range(5):
                if not cls.ssd_controller.write(lba=start_idx + i, value=value):
                    return MESSAGE_FAIL
            for i in range(5):
                if value != cls.ssd_controller.read(lba=start_idx + i):
                    return MESSAGE_FAIL

        cls.logging("... COMPLETE")
        return MESSAGE_PASS

    @classmethod
    def script_2(cls, num_iter: int = 30) -> str:
        lba_values: list[int] = [4, 0, 3, 1, 2]
        for _ in range(num_iter):
            value = utils.get_random_value()
            for lba in lba_values:
                success = cls.ssd_controller.write(lba, value)
                if not success:
                    return MESSAGE_FAIL

            for lba in lba_values:
                current_value = cls.ssd_controller.read(lba)
                if current_value == MESSAGE_ERROR:
                    return MESSAGE_FAIL
                if current_value != value:
                    return MESSAGE_FAIL

        cls.logging("... COMPLETE")
        return MESSAGE_PASS

    @classmethod
    def script_3(cls, num_iter: int = 200) -> str:
        lba_1, lba_2 = (0, SIZE_LBA - 1)
        for _ in range(num_iter):
            value = utils.get_random_value()
            cls.ssd_controller.write(lba=lba_1, value=value)
            cls.ssd_controller.write(lba=lba_2, value=value)
            if cls.ssd_controller.read(lba_1) != cls.ssd_controller.read(lba_2):
                return MESSAGE_FAIL

        cls.logging("... COMPLETE")
        return MESSAGE_PASS

    @classmethod
    def script_4(cls, num_iter: int = 30) -> str:
        ret = cls.command_executor.erase_range(0, 2)
        if MESSAGE_ERROR in ret:
            return MESSAGE_FAIL

        for _ in range(num_iter):
            for start_lba in range(2, SIZE_LBA - 1, 2):
                two_diff_values = utils.get_two_diff_random_value()

                for val in two_diff_values:
                    ret = cls.command_executor.write(start_lba, val)
                    if ret == MESSAGE_ERROR:
                        return MESSAGE_FAIL

                end_lba = min(start_lba + 2, SIZE_LBA - 1)
                ret = cls.command_executor.erase_range(start_lba, end_lba)
                if MESSAGE_ERROR in ret:
                    return MESSAGE_FAIL

        cls.logging("... COMPLETE")
        return MESSAGE_PASS


class Shell:
    logging: Callable = Logger().print
    shell_parser = ShellParser
    command_executor = CommandExecutor
    script_executor = ScriptExecutor
    _command_mapping_dict = None

    @classmethod
    def _command_mapper(cls, cmd: ShellCommandEnum):
        if cls._command_mapping_dict is None:
            cls._command_mapping_dict = {
                ShellCommandEnum.HELP: lambda: MESSAGE_HELP,
                ShellCommandEnum.READ: cls.command_executor.read,
                ShellCommandEnum.WRITE: cls.command_executor.write,
                ShellCommandEnum.FULLREAD: cls.command_executor.full_read,
                ShellCommandEnum.FULLWRITE: cls.command_executor.full_write,
                ShellCommandEnum.ERASE: cls.command_executor.erase,
                ShellCommandEnum.ERASE_RANGE: cls.command_executor.erase_range,
                ShellCommandEnum.FLUSH: cls.command_executor.flush,
                ShellCommandEnum.SCRIPT_1: cls.script_executor.script_1,
                ShellCommandEnum.SCRIPT_2: cls.script_executor.script_2,
                ShellCommandEnum.SCRIPT_3: cls.script_executor.script_3,
                ShellCommandEnum.SCRIPT_4: cls.script_executor.script_4,
                ShellCommandEnum.INVALID: lambda: MESSAGE_INVALID_SHELL_CMD
            }
        return cls._command_mapping_dict[cmd]

    @classmethod
    def execute_command(cls, cmd: ShellCommandEnum, args: list) -> Optional[str]:
        func = cls._command_mapper(cmd)
        return func(*args)

    @classmethod
    def run(cls) -> None:
        while True:
            cmd, args = cls.shell_parser.parse()
            if cmd is None:
                continue
            cls.logging(f"Command: {cmd.name} ({args})")
            if cmd == ShellCommandEnum.EXIT:
                break
            ret = cls.execute_command(cmd, args)
            if ret is not None:
                print(ret)

    @classmethod
    def run_script(cls, script: str = FILENAME_SCRIPT_DEFAULT) -> None:
        try:
            with open(cmd_file, "r") as f:
                cmds = f.readlines()

        except FileNotFoundError:
            print(MESSAGE_ERROR)
            return

        for cmd in cmds:
            cmd = cmd.strip()
            print(f"{cmd:<28}___   Run...", end="", flush=True)
            cmd_enum = cls.shell_parser.find_command(cmd)
            if cmd_enum == ShellCommandEnum.EXIT:
                break
            if cmd_enum is None:
                continue
            ret = cls.execute_command(cmd_enum, [])
            if ret is not None:
                if ret == MESSAGE_PASS:
                    print("Pass")
                else:
                    print("FAIL!")
                    break


if __name__ == "__main__":
    if len(sys.argv) == 2:
        cmd_file = sys.argv[1]
        Shell.run_script(script=cmd_file)
    else:
        Shell.run()
