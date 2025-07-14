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

def test_write_ssd():
    ssd = SSD()
    loc = 3
    ssd.write(loc, "0xFFFFFFFF")

    result = ssd.read(loc)
    assert result == "0xFFFFFFFF"

def test_write_check_file():
    ssd = SSD()
    loc = 11
    ssd.write(loc, "0x1298CDEF")

    with open("ssd_output.txt", "r") as f:
        content = f.read()
    assert content == ""

def test_out_of_index_error():
    ssd = SSD()
    loc = 120
    ssd.write(loc, "0x1298CDEF")

    with open("ssd_output.txt", "r") as f:
        content = f.read()
    assert content == "ERROR"

