from command_buffer import BufferManager


def test_bufferManager_flow():
    bm = BufferManager()

    buffers = bm.get_buffer()
    buffers = []
    bm.set_buffer(buffers)
    assert bm.get_buffer() == []
