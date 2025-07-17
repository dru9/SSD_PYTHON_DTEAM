import os
import sys

from command_buffer import BufferManager, Buffer
from constant import FILENAME, FILENAME_OUT, SIZE_LBA


class FileManager:
    def __init__(self):
        self.init_nand_txt()

    def init_nand_txt(self):
        if not os.path.exists(FILENAME):
            with open(FILENAME, "w") as f:
                for i in range(SIZE_LBA):
                    f.write(f"{i}\t0x00000000\n")

    def _read_whole_contents_nand_txt(self) -> dict[int, str]:
        result = {}
        with open(FILENAME, "r") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue  # 빈 줄 무시
                parts = line.split("\t")
                if len(parts) != 2:
                    continue
                result[int(parts[0])] = parts[1]
        return result

    def _save_to_nand_file(self, data) -> None:
        with open(FILENAME, "w") as f:
            for key, value in data.items():
                f.write(f"{key}\t{value}\n")

    def read_nand_txt(self, lba):
        data_list = self._read_whole_contents_nand_txt()
        return data_list.get(lba, "")

    def write_nand_txt(self, lba, change_data) -> bool:
        nand_datas = self._read_whole_contents_nand_txt()
        current_data = nand_datas.get(lba, "")
        if current_data == "":
            return False
        nand_datas[lba] = change_data
        self._save_to_nand_file(nand_datas)
        return True

    def erase_nand_txt(self, lba, size) -> bool:
        nand_datas = self._read_whole_contents_nand_txt()
        current_data = nand_datas.get(lba, "")
        if current_data == "":
            return False
        for each_lba in range(lba, lba + size):
            nand_datas[each_lba] = "0x00000000"
        self._save_to_nand_file(nand_datas)
        return True

    def write_output_txt(self, contents: str):
        with open(FILENAME_OUT, "w") as f:
            f.write(contents)


class SSD:
    def __init__(self, file_manager):
        self.file_manager = file_manager
        self.buffer_manager = BufferManager()

    def read(self, lba):
        read_value = self.file_manager.read_nand_txt(lba)
        if read_value == "":
            self.file_manager.write_output_txt("ERROR")
        else:
            self.file_manager.write_output_txt(read_value)

    def write(self, lba, data):
        if not self.file_manager.write_nand_txt(lba, data):
            self.file_manager.write_output_txt("ERROR")
        self.file_manager.write_output_txt("")

    def check_hex(self, data):
        if len(data) != 10:
            return False
        if not data[:2] == "0x":
            return False
        try:
            int(data[2:], 16)
            return True
        except ValueError:
            return False

    def _index_valid(self, num):
        return num.isdigit() and 0 <= int(num) <= SIZE_LBA - 1

    def _parse_int_or_empty(self, num):
        try:
            return int(num)
        except ValueError:
            return ""

    def execute_command(self, args):
        if not self._args_valid_guard_clauses(args):
            return

        mode = args[1]

        if mode == "F":
            self._execute_command_with_buffers(mode=mode)
        else:
            lba = int(args[2])
            if mode == "W":
                hex_string = args[3]
                self._execute_command_with_buffers(mode=mode, lba=lba, data=hex_string)
            elif mode == "R":
                self._execute_command_with_buffers(mode=mode, lba=lba)
            elif mode == "E":
                size = self._parse_int_or_empty(args[3])
                self._execute_command_with_buffers(mode=mode, lba=lba, erase_size=size)

    def erase(self, lba, size):
        if not self.file_manager.erase_nand_txt(lba, size):
            self.file_manager.write_output_txt("ERROR")
        self.file_manager.write_output_txt("")

    def _args_valid_guard_clauses(self, args):
        def _error(message):
            print(message)
            self.file_manager.write_output_txt("ERROR")
            return False

        argument_len = len(args)
        if argument_len < 2:
            return _error("At least one argument are required")

        mode = args[1]
        valid_modes = {"W", "R", "E", "F"}
        if mode not in valid_modes:
            return _error("Mode should be in ('W', 'R', 'E', 'F')")

        # mode별 기대하는 argument 개수와 메시지
        expected_args = {
            "W": (4, "Mode W need lba and value"),
            "R": (3, "Mode R need lba"),
            "E": (4, "Mode E need lba and size"),
            "F": (2, "Mode F need only command"),
        }

        expected_len, error_msg = expected_args[mode]
        if argument_len != expected_len:
            return _error(error_msg)

        if mode == "F":
            return True

        lba = self._parse_int_or_empty(args[2])
        if lba == "" or not self._index_valid(args[2]):
            return _error("The index should be an integer among 0 ~ 99")

        if mode == "W" and not self.check_hex(args[3]):
            return _error("Value should to be hex string")

        if mode == "E":
            size = self._parse_int_or_empty(args[3])
            if size == "" or size < 1 or size > 10 or lba + size > SIZE_LBA:
                return _error("Size should be integer among 1 ~ 10 and lba + size must be smaller than 101")

        return True

    def flush(self, buffers):
        for buffer in buffers:
            if buffer.command == "W":
                self.write(buffer.lba, buffer.data)
            elif buffer.command == "E":
                self.erase(buffer.lba, buffer.range)
            else:
                self.file_manager.write_output_txt("ERROR")
                print("Invalid command")
                break
        self.buffer_manager.set_buffer([])

    def _process_read_mode(self, buffers, lba):
        if not self.read_buffer_first(buffers, lba):
            self.read(lba)

    def _execute_command_with_buffers(self, mode, lba=None, data='', erase_size=0):
        buffers = self.buffer_manager.get_buffer()
        buffers = self._flush_when_buffer_are_full_or_flush_mode(buffers, mode)
        if mode == "F":
            self.file_manager.write_output_txt("")
            return

        if mode == "R":
            self._process_read_mode(buffers, lba)
            return
        # W
        new_buffers = []
        new_buffer = Buffer(mode, lba, data, erase_size)
        is_need_append_new_buffer = True
        if mode == "W":
            is_need_append_new_buffer, new_buffers = self._process_write_mode(buffers, is_need_append_new_buffer, lba,
                                                                              new_buffer, new_buffers)
        # E
        if mode == "E":
            is_need_append_new_buffer, new_buffers = self._process_erase_mode(buffers, erase_size,
                                                                              is_need_append_new_buffer, lba,
                                                                              new_buffer, new_buffers)

        if is_need_append_new_buffer:
            new_buffers.append(new_buffer)
        # 마지막에 rename
        self.buffer_manager.set_buffer(new_buffers)
        self.file_manager.write_output_txt("")

    def _process_erase_mode(self, buffers, erase_size, is_need_append_new_buffer, lba, new_buffer, new_buffers):
        for i, each_buffer in enumerate(buffers):
            # 1. W인 경우
            if each_buffer.command == "W":
                if lba <= each_buffer.lba < lba + erase_size:
                    continue
                new_buffers.append(each_buffer)
                continue
            # 2. E인 경우
            if each_buffer.command == "E":
                # erase 범위가 완전 동일한 경우
                if each_buffer.lba == lba and each_buffer.lba + each_buffer.range == lba + erase_size:
                    new_buffers += buffers[i + 1:]
                    new_buffers.append(new_buffer)
                    is_need_append_new_buffer = False
                    break
                # erase 범위가 겹치는 경우

                elif ((each_buffer.lba <= lba < each_buffer.lba + each_buffer.range) or
                      (lba <= each_buffer.lba < lba + erase_size)):

                    # range 합쳤을 때, 10 넘는 경우에는 합치지 않기
                    min_lba = lba
                    if lba > each_buffer.lba :
                        min_lba = each_buffer.lba
                    max_range = lba + erase_size
                    if max_range < each_buffer.lba + each_buffer.range :
                        max_range = each_buffer.lba + each_buffer.range
                    if max_range - min_lba > 10 :
                        new_buffers.append(each_buffer)
                        continue

                    if each_buffer.lba <= lba:
                        # b.lba + b.range > 100 또는 lba + erase_size > 100  넘는 경우에도 추가하면 안돼!
                        if lba + erase_size > SIZE_LBA or each_buffer.lba + each_buffer.range > SIZE_LBA:
                            new_buffers.append(each_buffer)
                            continue

                        if each_buffer.lba + each_buffer.range > lba + erase_size:
                            new_buffers += buffers[i:]
                            is_need_append_new_buffer = False
                            break

                        each_buffer.range = lba + erase_size - each_buffer.lba
                        new_buffers += buffers[i + 1:]
                        new_buffers.append(each_buffer)
                        is_need_append_new_buffer = False
                        break

                    if lba < each_buffer.lba:
                        # lba + range  > 100 or b.lba + b.range > 100 넘는 경우에도 추가하면 안돼
                        if lba + erase_size > SIZE_LBA or each_buffer.lba + each_buffer.range > SIZE_LBA:
                            new_buffers.append(each_buffer)
                            continue

                        new_range = each_buffer.lba + each_buffer.range - lba
                        if new_range > erase_size:
                            new_buffer.range = new_range

                        continue
                new_buffers.append(each_buffer)
                continue
        return is_need_append_new_buffer, new_buffers

    def _process_write_mode(self, buffers, is_need_append_new_buffer, lba, new_buffer, new_buffers):
        for i, each_buffer in enumerate(buffers):
            # 1. W인 경우
            if each_buffer.command == "W":
                if each_buffer.lba != lba:
                    new_buffers.append(each_buffer)
                    continue
                new_buffers += buffers[i + 1:]
                new_buffers.append(new_buffer)
                is_need_append_new_buffer = False
                break
            # 2. E인 경우
            if each_buffer.command == "E":
                if each_buffer.lba == lba:
                    if each_buffer.range == 1:
                        new_buffers += buffers[i + 1:]
                        new_buffers.append(new_buffer)
                        is_need_append_new_buffer = False
                        break
                    each_buffer.lba += 1
                    each_buffer.range -= 1
                elif (each_buffer.lba + each_buffer.range - 1) == lba:
                    each_buffer.range -= 1
                new_buffers.append(each_buffer)
                continue
        return is_need_append_new_buffer, new_buffers

    def read_buffer_first(self, buffers, lba):
        for _, each_buffer in reversed(list(enumerate(buffers))):
            if each_buffer.command == "W":
                if each_buffer.lba == lba:
                    self.file_manager.write_output_txt(each_buffer.data)
                    return True
            if each_buffer.command == "E":
                if self.check_read_lba_is_in_erase_range(each_buffer, lba):
                    self.file_manager.write_output_txt("0x00000000")
                    return True
        return False

    def check_read_lba_is_in_erase_range(self, buffer, lba):
        return buffer.lba <= lba < buffer.lba + buffer.range

    def _flush_when_buffer_are_full_or_flush_mode(self, buffers, mode):
        # flush 조건 체크
        if len(buffers) == 5 or mode == "F":
            self.flush(buffers)
            buffers = self.buffer_manager.get_buffer()
        return buffers


if __name__ == "__main__":
    ssd = SSD(FileManager())
    ssd.execute_command(sys.argv)
