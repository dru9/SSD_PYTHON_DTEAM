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
        return num.isdigit() and int(num) >= 0 and int(num) <= SIZE_LBA - 1

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
            buffers = self.buffer_manager.get_buffer()
            self.flush(buffers)
            self.file_manager.write_output_txt("")
            return
        lba = int(args[2])
        if mode == "W":
            hex = args[3]
            self._execute_command_new(mode=mode, lba=lba, data=hex)
        elif mode == "R":
            self._execute_command_new(mode=mode, lba=lba)
        elif mode == "E":
            size = self._parse_int_or_empty(args[3])
            self._execute_command_new(mode=mode, lba=lba, erase_size=size)

    def erase(self, lba, size):
        if not self.file_manager.erase_nand_txt(lba, size):
            self.file_manager.write_output_txt("ERROR")
        self.file_manager.write_output_txt("")

    def _args_valid_guard_clauses(self, args):
        argument_len = len(args)
        if argument_len < 2:
            print("At least one argument are required")
            self.file_manager.write_output_txt("ERROR")
            return False

        mode = args[1]
        if mode not in ("W", "R", "E", "F"):
            print("Mode should be in ('W', 'R', 'E', 'F')")
            self.file_manager.write_output_txt("ERROR")
            return False

        if mode == "W" and argument_len != 4:
            print("Mode W need lba and value")
            self.file_manager.write_output_txt("ERROR")
            return False

        if mode == "R" and argument_len != 3:
            print("Mode R need lba")
            self.file_manager.write_output_txt("ERROR")
            return False

        if mode == "E" and argument_len != 4:
            print("Mode E need lba and size")
            self.file_manager.write_output_txt("ERROR")
            return False

        if mode == "F" and argument_len != 2:
            print("Mode F need only command")
            self.file_manager.write_output_txt("ERROR")
            return False

        if mode == "F":
            return True

        lba = self._parse_int_or_empty(args[2])

        if lba == "" or not self._index_valid(args[2]):
            print("The index should be an integer among 0 ~ 99")
            self.file_manager.write_output_txt("ERROR")
            return False

        if mode == "W" and not self.check_hex(args[3]):
            print("Value should to be hex string")
            self.file_manager.write_output_txt("ERROR")
            return False

        if mode == "E":
            size = self._parse_int_or_empty(args[3])
            if size == "" or size < 1 or size > 10 or lba + size > SIZE_LBA:
                print("Size should be integer among 1 ~ 10 and lba + size must be smaller than 101")
                self.file_manager.write_output_txt("ERROR")
                return False
        return True

    def flush(self, buffers):
        for buffer in buffers:
            if buffer.command == "W":
                self.write(buffer.lba, buffer.data)
            elif buffer.command == "E":
                self.read(buffer.lba)
            else:
                self.file_manager.write_output_txt("ERROR")
                print("Invalid command")
                break
        self.buffer_manager.set_buffer([])

    def _execute_command_new(self, mode, lba: int, data='', erase_size=0):
        buffers = self.buffer_manager.get_buffer()
        # flush 조건 체크
        if len(buffers) == 5:
            self.flush(buffers)
            buffers = self.buffer_manager.get_buffer()

        # Buffer에 접근 먼저 해서 알고리즘 동작하게 하기.
        # R
        if mode == "R":
            for i, b in enumerate(buffers):
                if b.command == "W":
                    if b.lba == lba:
                        self.file_manager.write_output_txt(b.data)
                        return
                if b.command == "E":
                    if lba >= b.lba and lba < b.lba + b.range:
                        self.file_manager.write_output_txt("0x00000000")
                        return
            self.read(lba)
            return
        # W
        new_buffers = []
        new_buffer = Buffer(mode, lba, data, erase_size)
        is_need_append_new_buffer = True
        if mode == "W":
            for i, b in enumerate(buffers):
                # 1. W인 경우
                if b.command == "W":
                    if b.lba != lba:
                        new_buffers.append(b)
                        continue
                    new_buffers += buffers[i + 1:]
                    new_buffers.append(new_buffer)
                    is_need_append_new_buffer = False
                    break
                # 2. E인 경우
                if b.command == "E":
                    if b.lba == lba:
                        if b.range == 1:
                            new_buffers += buffers[i + 1:]
                            new_buffers.append(new_buffer)
                            is_need_append_new_buffer = False
                            break
                        b.lba += 1
                        b.range -= 1
                    elif (b.lba + b.range - 1) == lba:
                        b.range -= 1
                    new_buffers.append(b)
                    continue
        # E
        if mode == "E":
            for i, b in enumerate(buffers):
                # 1. W인 경우
                if b.command == "W":
                    if b.lba >= lba and b.lba < lba + erase_size:
                        continue
                    new_buffers.append(b)
                    continue
                # 2. E인 경우
                if b.command == "E":
                    # erase 범위가 완전 동일한 경우
                    if b.lba == lba and b.lba + b.range == lba + erase_size:
                        new_buffers += buffers[i + 1:]
                        new_buffers.append(new_buffer)
                        is_need_append_new_buffer = False
                        break
                    # erase 범위가 겹치는 경우
                    elif ((b.lba <= lba and b.lba + b.range > lba) or
                          (b.lba >= lba and b.lba < lba + erase_size)):
                        # range 합쳤을 때, 10 넘는 경우에는 합치지 않기
                        min_lba = b.lba
                        if b.lba > lba:
                            min_lba = lba
                        max_range = lba + erase_size -1
                        if max_range < b.lba + b.range -1:
                            max_range = b.lba + b.range -1

                        if max_range - min_lba > 10:
                            new_buffers.append(b)
                            continue

                        if b.lba <= lba:
                            # b.lba + b.range > 100 또는 lba + erase_size > 100  넘는 경우에도 추가하면 안돼!
                            if lba + erase_size > SIZE_LBA or b.lba + b.range > SIZE_LBA:
                                new_buffers.append(b)
                                continue

                            if b.lba + b.range > lba + erase_size:
                                new_buffers += buffers[i:]
                                is_need_append_new_buffer = False
                                break

                            b.range = lba + erase_size - b.lba
                            new_buffers += buffers[i + 1:]
                            new_buffers.append(b)
                            is_need_append_new_buffer = False
                            break

                        if lba < b.lba:
                            # lba + range  > 100 or b.lba + b.range > 100 넘는 경우에도 추가하면 안돼
                            if lba + erase_size > SIZE_LBA or b.lba + b.range > SIZE_LBA:
                                new_buffers.append(b)
                                continue

                            new_buffer.range = b.lba + b.range - lba
                            continue
                    new_buffers.append(b)
                    continue

        if is_need_append_new_buffer:
            new_buffers.append(new_buffer)
        # 마지막에 rename
        self.buffer_manager.set_buffer(new_buffers)
        self.file_manager.write_output_txt("")


if __name__ == "__main__":
    ssd = SSD(FileManager())
    ssd.execute_command(sys.argv)
