import os
import sys
from filelock import Timeout, FileLock
from constant import FILENAME, FILENAME_OUT, FILENAME_LOCK, FILENAME_OUT_LOCK


class FileManager:
    def __init__(self):
        self.filename_lock = FileLock(FILENAME_LOCK, timeout=10)
        self.filename_out_lock = FileLock(FILENAME_OUT_LOCK, timeout=10)
        self.init_nand_txt()

    def init_nand_txt(self):
        if not os.path.exists(FILENAME):
            with open(FILENAME, "w") as f:
                for i in range(100):
                    f.write(f"{i}\t0x00000000\n")

    def _read_whole_contents_nand_txt(self) -> dict[int, str]:

        result = {}

        with self.filename_lock:
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
        with self.filename_lock:
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

    def write_output_txt(self, contents: str):
        with self.filename_out_lock:
            with open(FILENAME_OUT, "w") as f:
                f.write(contents)


class SSD:
    def __init__(self, file_manager):
        self.file_manager = file_manager

    def read(self, lba):
        if lba < 0 or lba > 99:
            self.file_manager.write_output_file("ERROR")
            return
        read_value = self.file_manager.read_nand_txt(lba)
        if read_value == "":
            self.file_manager.write_output_txt("ERROR")
        else:
            self.file_manager.write_output_txt(read_value)

    def write(self, lba, data):
        if lba < 0 or lba > 99:
            self.file_manager.write_output_txt("ERROR")
            return

        if not self.file_manager.write_nand_txt(lba, data):
            self.file_manager.write_output_txt("ERROR")
        self.file_manager.write_output_txt("")


def check_hex(data):
    if len(data) != 10:
        return False
    if not data[:2] == "0x":
        return False
    try:
        int(data[2:], 16)
        return True
    except ValueError:
        return False


if __name__ == "__main__":
    args = sys.argv
    argument_len = len(args)
    if argument_len < 3:
        print("At least two argument are required")
        sys.exit(1)
    if not args[2].isdigit() or (int(args[2]) < 0) or (int(args[2]) > 99):
        print("The index should be an integer among 0 ~ 99")
        sys.exit(1)

    ssd = SSD(FileManager())
    mode = sys.argv[1]
    lba = int(sys.argv[2])
    if mode == "W" and len(sys.argv) == 4:

        ssd.write(lba, sys.argv[3])
    elif mode == "R" and argument_len == 3:
        ssd.read(lba)
    else:
        print("Invalid argument")
