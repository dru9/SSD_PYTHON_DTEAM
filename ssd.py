
import os

FILE_PATH = "ssd_nand.txt"
OUT_FILE_PATH = "ssd_output.txt"

class SSD:
    def __init__(self):
        if not os.path.exists(FILE_PATH):
            with open(FILE_PATH, "w") as f:
                for i in range(100):
                    f.write(f"{i}\t0x00000000\n")

        self.contents = ""
        with open(FILE_PATH,"r") as f:
            self.contents += f.readline()

    def read(self, LBA):
        pass

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
        data_list[LBA] = data
        self.dict_to_file(data_list)
        self.write_output_file("")
