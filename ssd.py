
import os

FILE_PATH = "ssd_nand.txt"

class SSD:
    def __init__(self):
        if not os.path.exists(FILE_PATH):
            with open(FILE_PATH, "w") as f:
                for i in range(100):
                    f.write(f"{i}\t0x00000000\n")

    def read(self, LBA):
        pass

    def write(self, LBA, data):
        pass

