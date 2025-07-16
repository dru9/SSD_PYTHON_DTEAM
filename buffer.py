@property
class Buffer:
    def __init__(self):
        self.index = 0
        self.command = ''
        self.lba = 0
        self.data = ''  # Write 용
        self.range = 0  # Erase 용


class BufferManager:
    def __init__(self):
        self.buffers = []  # list[Buffer]
        # ./buffer dir + empty 파일 5개 없으면 만드는 함수 필요.

    def get_buffer(self) -> list[Buffer]:
        # 파일 읽어서 버퍼로 만들어 주는 역할

    def set_buffer(self, buffers: list[Buffer]):
        # execute 후 self.buffers에 내용 바꾸는 역할

    def _rename_buffers_to_files(self):
        # self.buffers 내용 바뀔 때 rename 하는 역할

    def _get_files_to_buffers(self):
        # ./buffer directory 내의 buffer 파일 name가져와서 self.buffers에 등록하는 역할

