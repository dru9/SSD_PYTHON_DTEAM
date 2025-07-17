import os
from pathlib import Path

BUFFER_INDEX = 5
BUFFER_FOLDER = "./buffer"


class Buffer:
    def __init__(self, command='', lba=0, data='', range=0):
        self.command = command
        self.lba = lba
        self.data = data  # Write 용
        self.range = range  # Erase 용

    def to_string(self, idx):
        if self.command == 'W':
            return f'{idx}_{self.command}_{self.lba}_{self.data}'
        elif self.command == 'E':
            return f'{idx}_{self.command}_{self.lba}_{self.range}'
        return f'{idx}_empty'


class BufferManager:
    def __init__(self):
        self.buffers: list[Buffer] = []
        # ./buffer dir + empty 파일 5개 없으면 만듬
        self.make_empty_buffer_folder_and_files()
        self._get_files_to_buffers()

    def _find_prefix_in_strlist(self, prefix, str_list):
        for str in str_list:
            if str.startswith(prefix):
                return True
        return False
    def make_empty_buffer_folder_and_files(self):
        if not os.path.exists(BUFFER_FOLDER):
            os.makedirs(BUFFER_FOLDER)
        file_list = os.listdir(BUFFER_FOLDER)
        for buffer_idx in range(1, BUFFER_INDEX + 1):
            if self._find_prefix_in_strlist(str(buffer_idx), file_list):
                continue
            self.make_buffer_file(str(buffer_idx) + "_empty")

    def get_buffer(self) -> list[Buffer]:
        self._get_files_to_buffers()
        return self.buffers

    def set_buffer(self, buffers: list[Buffer]):
        self.buffers = buffers
        self._rename_buffers_to_files()

    def _rename_buffers_to_files(self):
        for filename in os.listdir(BUFFER_FOLDER):
            file_path = os.path.join(BUFFER_FOLDER, filename)
            os.remove(file_path)

        # Rename
        for idx, buffer in enumerate(self.buffers):
            self.make_buffer_file(buffer.to_string(idx + 1))

        for empty_idx in range(len(self.buffers) + 1, BUFFER_INDEX + 1):
            self.make_buffer_file(str(empty_idx) + '_empty')

    def make_buffer_file(self, file_name):
        filepath = BUFFER_FOLDER + "/" + file_name
        file = Path(filepath)
        file.touch()

    def _get_files_to_buffers(self):
        # ./buffer directory 내의 buffer 파일 name가져와서 self.buffers에 등록하는 역할
        self.buffers = []  # 비우고 시작

        file_list = os.listdir(BUFFER_FOLDER)
        file_list.sort()
        for fileName in file_list:
            if "empty" in fileName:
                continue

            chunks = fileName.split("_")
            if len(chunks) < 4:
                continue

            new_buffer = Buffer(command=chunks[1], lba=int(chunks[2]), data='', range=0)
            if new_buffer.command == "W":
                new_buffer.data = chunks[3]
            elif new_buffer.command == "E":
                new_buffer.range = int(chunks[3])
            else:
                continue
            self.buffers.append(new_buffer)
