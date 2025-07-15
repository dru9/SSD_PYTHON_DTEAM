import os
import sys

FILE_PATH = "ssd_nand.txt"
OUT_FILE_PATH = "ssd_output.txt"


class FileManager:
    def _read_whole_contents_nand_txt(self):
        pass

    def read_nand_txt(self, lba):
        pass

    def write_nand_txt(self, lba, data):
        pass

    def write_output_txt(self, contents: str):
        pass


class SSD:
    def __init__(self, file_manager):
        if not os.path.exists(FILE_PATH):
            with open(FILE_PATH, "w") as f:
                for i in range(100):
                    f.write(f"{i}\t0x00000000\n")

        self.contents = ""
        with open(FILE_PATH, "r") as f:
            self.contents += f.readline()
        self.file_manager = file_manager

    def read(self, LBA):
        if LBA < 0 or LBA > 99:
            self.write_output_file("ERROR")
            return

        data_list = self.file_to_dict()
        if data_list == "":
            self.write_output_file("ERROR")
        self.dict_to_file(data_list)
        self.write_output_file(data_list[LBA])

    def file_to_dict(self):
        result = {}
        with open(FILE_PATH, "r") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue  # 빈 줄 무시
                parts = line.split("\t")
                if len(parts) >= 2:
                    key = int(parts[0])
                    value = parts[1]
                    result[key] = value
        return result

    def dict_to_file(self, data):
        with open(FILE_PATH, "w") as f:
            for key, value in data.items():
                f.write(f"{key}\t{value}\n")

    def write_output_file(self, str):
        with open(OUT_FILE_PATH, "w") as f:
            f.write(str)

    def write(self, LBA, data):
        if LBA < 0 or LBA > 99:
            self.write_output_file("ERROR")
            return

        data_list = self.file_to_dict()
        data_list.get(LBA, "")
        if data_list == "":
            self.write_output_file("ERROR")
        data_list[LBA] = data
        self.dict_to_file(data_list)
        self.write_output_file("")


def check_hex(data):
    if len(data) < 10:
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

    mode = args[1]
    LBA = int(args[2])
    ssd = SSD(FileManager())

    if mode == "W" and check_hex(args[3]) and argument_len == 4:
        ssd.write(LBA, sys.argv[3])
    elif mode == "R" and argument_len == 3:
        ssd.read(LBA)
    else:
        print("Invalid argument")
