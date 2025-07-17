import os
import sys
from typing import Any, Mapping

import utils
from command_buffer import BufferManager, Buffer
from constant import FILENAME, FILENAME_OUT, SIZE_LBA


class FileManager:

    def __init__(self) -> None:
        self.init_nand()

    @classmethod
    def init_nand(cls) -> None:
        if os.path.exists(FILENAME):
            return

        with open(FILENAME, "w") as f:
            for i in range(SIZE_LBA):
                f.write(f"{i}\t0x00000000\n")

    @classmethod
    def _read_whole_lines(cls) -> dict[int, str]:
        result = {}
        with open(FILENAME, "r") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                parts = line.split("\t")
                if len(parts) != 2:
                    continue
                result[int(parts[0])] = parts[1]
        return result

    @classmethod
    def _save_to_nand(cls, data) -> None:
        with open(FILENAME, "w") as f:
            for key, value in data.items():
                f.write(f"{key}\t{value}\n")

    @classmethod
    def read_nand(cls, lba):
        data_list = cls._read_whole_lines()
        return data_list.get(lba, "")

    @classmethod
    def write_nand(cls, lba, change_data) -> bool:
        nand_datas = cls._read_whole_lines()
        current_data = nand_datas.get(lba, "")
        if current_data == "":
            return False
        nand_datas[lba] = change_data
        cls._save_to_nand(nand_datas)
        return True

    @classmethod
    def erase_nand(cls, lba, size) -> bool:
        lines = cls._read_whole_lines()
        current_data = lines.get(lba, "")
        if current_data == "":
            return False
        for each_lba in range(lba, lba + size):
            lines[each_lba] = "0x00000000"
        cls._save_to_nand(lines)
        return True

    @classmethod
    def write_output(cls, contents: str):
        with open(FILENAME_OUT, "w") as f:
            f.write(contents)


class SSD:

    def __init__(self) -> None:
        self.file_manager = FileManager()
        self.buffer_manager = BufferManager()

    def read(self, lba) -> None:
        read_value = self.file_manager.read_nand(lba)
        if read_value == "":
            self.file_manager.write_output("ERROR")
        else:
            self.file_manager.write_output(read_value)

    def write(self, lba, data) -> None:
        if not self.file_manager.write_nand(lba, data):
            self.file_manager.write_output("ERROR")
        self.file_manager.write_output("")

    def erase(self, lba, size) -> None:
        if not self.file_manager.erase_nand(lba, size):
            self.file_manager.write_output("ERROR")
        self.file_manager.write_output("")

    def flush(self, buffers: list[Buffer]) -> None:
        for buffer in buffers:
            if buffer.command == "W":
                self.write(buffer.lba, buffer.data)
            elif buffer.command == "E":
                self.erase(buffer.lba, buffer.range)
            else:
                self.file_manager.write_output("ERROR")
                print("Invalid command")
                break
        self.buffer_manager.set_buffer([])

    def execute(self, args) -> None:
        if not self._validate_cmd_args(args):
            return

        mode = args[1]
        kwargs: dict[str, Any] = {"mode": mode}
        if mode == "R":
            kwargs.update({"lba": int(args[2])})
        elif mode == "W":
            kwargs.update({"lba": int(args[2]), "data": args[3]})
        elif mode == "E":
            kwargs.update({"lba": int(args[2]), "erase_size": utils.parse_integer(args[3])})
        else:
            pass

        self._execute_command(**kwargs)

    def _validate_cmd_args(self, args):

        def check_error(msg: str) -> None:
            print(msg)
            self.file_manager.write_output("ERROR")

        length = len(args)
        if length < 2:
            check_error("At least one argument are required")
            return False

        mode = args[1]
        valid_modes = {"W", "R", "E", "F"}
        if mode not in valid_modes:
            check_error(f"Invalid mode not in {valid_modes}")
            return False

        expected_args = {
            "W": (4, "Mode W need lba and value"),
            "R": (3, "Mode R need lba"),
            "E": (4, "Mode E need lba and size"),
            "F": (2, "Mode F need only command"),
        }
        expected_len, error_msg = expected_args[mode]
        if length != expected_len:
            check_error(error_msg)
            return False

        if mode == "F":
            return True

        lba = utils.parse_integer(args[2])
        if lba == "" or not utils.validate_index(args[2], valid_size=SIZE_LBA):
            check_error("The index should be an integer among 0 ~ 99")
            return False

        if mode == "W" and not utils.validate_hexadecimal(args[3]):
            check_error("Value should to be hex string")
            return False

        if mode == "E":
            size = utils.parse_integer(args[3])
            if size == "" or size < 1 or size > 10 or lba + size > SIZE_LBA:
                check_error("Size should be integer among 1 ~ 10 and lba + size must be smaller than 101")
                return False

        return True

    def _execute_command(self, mode, lba=None, data='', erase_size=0):
        buffers = self.buffer_manager.get_buffer()
        buffers = self._flush_when_buffer_are_full_or_flush_mode(buffers, mode)
        if mode == "F":
            self.file_manager.write_output("")
            return

        if mode == "R":
            self._process_read_mode(buffers, lba)
            return

        new_buffer = Buffer(mode, lba, data, erase_size)
        if mode == "W":
            new_buffers = self._process_write_mode(buffers, lba, new_buffer)
        elif mode == "E":
            new_buffers = self._process_erase_mode(buffers, erase_size, lba, new_buffer)
        else:
            return

        self.buffer_manager.set_buffer(new_buffers)
        self.file_manager.write_output("")

    def _process_read_mode(self, buffers, lba):
        """Conditionally read from the first buffer."""
        from_first_buffer: bool = False
        for _, buffer in reversed(list(enumerate(buffers))):
            if buffer.command == "W" and buffer.lba == lba:
                self.file_manager.write_output(buffer.data)
                from_first_buffer = True
                break

            if buffer.command == "E" and buffer.lba <= lba < buffer.lba + buffer.range:
                self.file_manager.write_output("0x00000000")
                from_first_buffer = True
                break

        if not from_first_buffer:
            self.read(lba)

    def _process_erase_mode(self, buffers, erase_size, lba, new_buffer):
        def _is_erase_range_same(each_buffer, erase_size, lba):
            return each_buffer.lba == lba and each_buffer.lba + each_buffer.range == lba + erase_size

        def _is_erase_range_overlap(each_buffer, erase_size, lba):
            return ((each_buffer.lba <= lba < each_buffer.lba + each_buffer.range) or
                    (lba <= each_buffer.lba < lba + erase_size))

        def _check_merge_range_is_bigger_than_10(each_buffer, erase_size, lba):
            min_lba = min(lba, each_buffer.lba)
            max_range = lba + erase_size
            if max_range < each_buffer.lba + each_buffer.range:
                max_range = each_buffer.lba + each_buffer.range
            if max_range - min_lba > 10:
                return True
            else:
                return False

        def _continue_check_for_erase_range_overlap(each_buffer, erase_size, lba, new_buffers):
            if _check_merge_range_is_bigger_than_10(each_buffer, erase_size, lba):
                new_buffers.append(each_buffer)
                return True
            if each_buffer.lba <= lba:
                # b.lba + b.range > 100 또는 lba + erase_size > 100  넘는 경우에도 추가하면 안돼!
                if lba + erase_size > SIZE_LBA or each_buffer.lba + each_buffer.range > SIZE_LBA:
                    new_buffers.append(each_buffer)
                    return True
            else:
                # lba + range  > 100 or b.lba + b.range > 100 넘는 경우에도 추가하면 안돼
                if lba + erase_size > SIZE_LBA or each_buffer.lba + each_buffer.range > SIZE_LBA:
                    new_buffers.append(each_buffer)
                    return True
            return False

        new_buffers = []
        is_need_to_append = True
        for i, each_buffer in enumerate(buffers):
            if each_buffer.command == "W":
                if lba > each_buffer.lba or each_buffer.lba >= lba + erase_size:
                    new_buffers.append(each_buffer)
            elif each_buffer.command == "E":
                if _is_erase_range_same(each_buffer, erase_size, lba):
                    is_need_to_append, new_buffers = self.buffer_manager.update(buffers, i, new_buffer, new_buffers)
                    break
                elif _is_erase_range_overlap(each_buffer, erase_size, lba):
                    if _continue_check_for_erase_range_overlap(each_buffer, erase_size, lba, new_buffers):
                        continue

                    if each_buffer.lba <= lba:
                        if each_buffer.lba + each_buffer.range > lba + erase_size:
                            new_buffers += buffers[i:]
                            is_need_to_append = False
                            break

                        each_buffer.range = lba + erase_size - each_buffer.lba
                        is_need_to_append, new_buffers = self.buffer_manager.update(buffers, i, each_buffer, new_buffers)
                        break
                    else:
                        new_range = each_buffer.lba + each_buffer.range - lba
                        if new_range > erase_size:
                            new_buffer.range = new_range
        if is_need_to_append:
            new_buffers.append(new_buffer)
        return new_buffers

    def _process_write_mode(self, buffers, lba, new_buffer):
        def _handle_write(buffers, each_buffer, i, is_need_to_append, lba, new_buffer, new_buffers):
            if each_buffer.lba != lba:
                new_buffers.append(each_buffer)
            else:
                is_need_to_append, new_buffers = self.buffer_manager.update(buffers, i, new_buffer, new_buffers)
            return is_need_to_append, new_buffers

        def _handle_erase(buffers, each_buffer, i, is_need_to_append, lba, new_buffer, new_buffers):
            if each_buffer.lba == lba:
                if each_buffer.range == 1:
                    is_need_to_append, new_buffers = self.buffer_manager.update(buffers, i, new_buffer, new_buffers)
                if is_need_to_append:
                    each_buffer.lba += 1
                    each_buffer.range -= 1
            elif (each_buffer.lba + each_buffer.range - 1) == lba:
                each_buffer.range -= 1
            if is_need_to_append:
                new_buffers.append(each_buffer)
            return is_need_to_append, new_buffers

        new_buffers = []
        is_need_to_append = True
        for i, each_buffer in enumerate(buffers):
            if each_buffer.command == "W":
                is_need_to_append, new_buffers = _handle_write(
                    buffers,
                    each_buffer,
                    i,
                    is_need_to_append,
                    lba,
                    new_buffer,
                    new_buffers,
                )
            elif each_buffer.command == "E":
                is_need_to_append, new_buffers = _handle_erase(
                    buffers,
                    each_buffer,
                    i,
                    is_need_to_append,
                    lba,
                    new_buffer,
                    new_buffers,
                )
            if is_need_to_append == False:
                break

        if is_need_to_append:
            new_buffers.append(new_buffer)

        return new_buffers


    def _flush_when_buffer_are_full_or_flush_mode(self, buffers, mode):
        # flush 조건 체크
        if len(buffers) == 5 or mode == "F":
            self.flush(buffers)
            buffers = self.buffer_manager.get_buffer()
        return buffers


if __name__ == "__main__":
    ssd = SSD()
    ssd.execute(sys.argv)
