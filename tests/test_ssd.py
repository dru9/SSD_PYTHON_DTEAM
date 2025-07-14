import pytest
from ssd import SSD

def test_read_ssd_nand_txt_file_called_by_read():
    ssd = SSD()
    read_idx = 0
    ssd.read(read_idx)

    assert ssd.contents


def test_read_ssd_nand_txt_file_called_by_write():
    ssd = SSD()
    write_idx = 0
    write_contents = "0x00001111"
    ssd.write(write_idx, write_contents)

    assert ssd.contents

def test_read_method_record_ssd_output_txt():
    ssd = SSD()
    read_idx = 0
    ssd.read(read_idx)

    with open('./ssd_output.txt', 'r') as f:
        content = f.read()

    assert content == "0x00000000"


