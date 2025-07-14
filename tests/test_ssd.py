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