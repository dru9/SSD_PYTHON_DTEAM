import os
from typing import Optional
from pathlib import Path

BUFFER_INDEX = 5
BUFFER_FOLDER = "./buffer"


class Buffer:

    def __init__(self, command: str = "", lba: int = 0, data: str = "", range: int = 0) -> None:
        self.command = command
        self.lba = lba
        self.data = data
        self.range = range
        self.idx: Optional[int] = None

    def __str__(self) -> str:
        """This is pythonic."""
        if self.command == "W":
            return f"{self.idx}_{self.command}_{self.lba}_{self.data}"
        elif self.command == 'E':
            return f"{self.idx}_{self.command}_{self.lba}_{self.range}"
        else:
           return f"{self.idx}_empty"


class BufferManager:

    def __init__(self) -> None:
        self.buffers: list[Buffer] = []
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
            buffer.idx = idx + 1
            self.make_buffer_file(str(buffer))

        for empty_idx in range(len(self.buffers) + 1, BUFFER_INDEX + 1):
            self.make_buffer_file(str(empty_idx) + '_empty')

    def make_buffer_file(self, file_name):
        filepath = BUFFER_FOLDER + "/" + file_name
        file = Path(filepath)
        file.touch()

    def _get_files_to_buffers(self):
        """Register self.buffers from the filenames in the buffer directory."""
        self.buffers: list[Buffer] = []
        file_list = sorted(os.listdir(BUFFER_FOLDER))
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

    @classmethod
    def update(
            cls,
            buffers: list[Buffer],
            idx: int,
            new_buffer: Buffer,
            new_buffers: list[Buffer],
    ) -> tuple[bool, list[Buffer]]:
        new_buffers += buffers[idx + 1:]
        new_buffers.append(new_buffer)
        return False, new_buffers
