from command_buffer import BufferManager, Buffer


def test_bufferManager_flow1():
    bm = BufferManager()

    buffers = bm.get_buffer()
    buffers = []
    bm.set_buffer(buffers)
    assert bm.get_buffer() == []


def test_bufferManager_flow2():
    bm = BufferManager()
    buffers = bm.get_buffer()

    buffer1 = Buffer()
    buffer1.command = "W"
    buffer1.lba = 20
    buffer1.data = "0x12341234"

    buffer2 = Buffer()
    buffer2.command = "E"
    buffer2.lba = 10
    buffer2.range = 4
    buffers = [buffer1, buffer2]

    bm.set_buffer(buffers)
    new_buffers = bm.get_buffer()
    assert 2 == len(new_buffers)


def test_buffer_empty():
    buffer = Buffer()
    buffer.idx = 1
    expected = "1_empty"
    result = str(buffer)
    assert result == expected


def test_buffer_write():
    buffer = Buffer()
    buffer.command = "W"
    buffer.lba = 20
    buffer.data = "0x12341234"
    buffer.idx = 2
    expected = "2_W_20_0x12341234"
    result = str(buffer)
    assert result == expected


def test_buffer_erase():
    buffer = Buffer()
    buffer.command = "E"
    buffer.lba = 10
    buffer.range = 4
    buffer.idx = 2
    expected = "2_E_10_4"
    result = str(buffer)
    assert result == expected


def test_find_prefix():
    bm = BufferManager()
    file_names = ["2_0x12341234", "3_0x12341234", "4_0x12341234", "5_0x12341234"]

    result = bm._find_prefix_in_strlist("1", file_names)
    assert result == False

    file_names.append("1_0x12341234")
    result = bm._find_prefix_in_strlist("1", file_names)
    assert result == True
