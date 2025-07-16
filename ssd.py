import os
import sys

from constant import FILENAME, FILENAME_OUT


class FileManager:
    def __init__(self):
        self.init_nand_txt()

    def init_nand_txt(self):
        if not os.path.exists(FILENAME):
            with open(FILENAME, "w") as f:
                for i in range(100):
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
        return num.isdigit() and int(num) >= 0 and int(num) <= 99

    def _parse_int_or_empty(self, num):
        try:
            return int(num)
        except ValueError:
            return ""

    def execute_command(self, args):
        argument_len = len(args)
        if argument_len < 3:
            print("At least two argument are required")
            self.file_manager.write_output_txt("ERROR")
            return
        if not self._index_valid(args[2]):
            print("The index should be an integer among 0 ~ 99")
            self.file_manager.write_output_txt("ERROR")
            return

        mode = args[1]
        lba = self._parse_int_or_empty(args[2])
        if lba == "":
            self.file_manager.write_output_txt("ERROR")
            print("Invalid argument")
        if mode == "W" and self.check_hex(args[3]) and argument_len == 4:
            self.write(lba, args[3])
        elif mode == "R" and argument_len == 3:
            self.read(lba)
        elif mode == "E" and argument_len == 4:
            size = self._parse_int_or_empty(args[3])
            if size == "" or size < 1 or size > 10 or lba + size > 100:
                self.file_manager.write_output_txt("ERROR")
                print("Invalid argument")
            else:
                self.erase(lba, size)
        else:
            self.file_manager.write_output_txt("ERROR")
            print("Invalid argument")

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

    def _execute_command_new(self, args):
        buffers = self.buffer_manager.get_buffer()
        # flush 조건 체크

        # Buffer에 접근 먼저 해서 알고리즘 동작하게 하기.

        # 마지막에 rename
        self.buffer_manager.set_buffer(buffers)


if __name__ == "__main__":
    ssd = SSD(FileManager())
    ssd.execute_command(sys.argv)
