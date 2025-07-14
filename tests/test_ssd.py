
from ssd import SSD

def test_write_ssd():
    ssd = SSD()
    loc = 3
    ssd.write(loc, 0xFFFFFFFF)

    result = ssd.read(loc)
    assert result == 0xFFFFFFFF

def test_write_check_file():
    ssd = SSD()
    loc = 11
    ssd.write(loc, 0x1298CDEF)

    with open("ssd_output.txt", "r") as f:
        content = f.read()
    assert content == ""

def test_out_of_index_error():
    ssd = SSD()
    loc = 120
    ssd.write(loc, 0x1298CDEF)

    with open("ssd_output.txt", "r") as f:
        content = f.read()
    assert content == "ERROR"

