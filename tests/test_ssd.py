import pytest
from ssd import SSD
import re


def test_write():
    ssd = SSD()
    lba = 0
    expected = 0x12345678
    ssd.write(lba, expected)

    ssd.read(lba)
    f = open("./ssd_output.txt", 'r')
    actual = f.readline()
    f.close()

    assert expected == actual

def test_init_ssd_nand_file():
    ssd = SSD()
    for each_lba in range(0, 100):
        ssd.read(each_lba)
        f = open("./ssd_output.txt", 'r')
        actual = f.readline()
        f.close()
        assert "0x00000000" == actual

def test_valid_ssd_nand_file():
    def is_hex_string(text):
        pattern = r"^[0-9a-fA-F]+$"
        return bool(re.match(pattern, text))
    ssd = SSD()
    ssd.read(0)
    f = open("./ssd_output.txt", 'r')
    read_value = f.readline()
    f.close()

    assert is_hex_string(read_value)


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

