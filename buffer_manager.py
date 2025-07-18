import glob
import re
from pathlib import Path
from typing import Optional

BUFFER_INDEX = 5
BUFFER_DIRECTORY = "./buffer"


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
        self.path: Path = Path(BUFFER_DIRECTORY)
        self.buffers: list[Buffer] = []
        self._check_initial_buffer()
        self._register_buffer()

    def _check_initial_buffer(self) -> None:
        self.path.mkdir(parents=False, exist_ok=True)
        filenames = [p.name for p in self.path.iterdir()]
        for idx in range(1, BUFFER_INDEX + 1):
            pattern: re.Pattern = re.compile(rf"^{idx}_.*$")
            if any(pattern.match(f) for f in filenames):
                continue
            new = self.path / f"{idx}_empty"
            new.touch()

    def get_buffer(self) -> list[Buffer]:
        self._register_buffer()
        return self.buffers

    def set_buffer(self, buffers: list[Buffer]) -> None:
        self.buffers = buffers
        self._update_file()

    def _update_file(self) -> None:
        for filename in self.path.iterdir():
            filename.unlink(missing_ok=False)

        for idx, buffer in enumerate(self.buffers):
            buffer.idx = idx + 1
            filename = self.path / str(buffer)
            filename.touch()

        for idx in range(len(self.buffers) + 1, BUFFER_INDEX + 1):
            filename = self.path / f"{idx}_empty"
            filename.touch()

    def _register_buffer(self) -> None:
        """Register self.buffers from the filenames in the buffer directory."""
        buffers: list[Buffer] = []
        filenames = sorted(glob.glob(f"{self.path}/*"))
        for filename in filenames:
            if filename.endswith("empty"):
                continue

            args = filename.split("_")
            if len(args) < 4 or args[1] not in ["W", "E"]:
                continue

            cmd = args[1]
            kwargs = {"command": cmd, "lba": int(args[2]), "data": "", "range": 0}
            if cmd == "W":
                kwargs.update({"data": args[3]})
            if cmd == "E":
                kwargs.update({"range": int(args[3])})
            buffers.append(Buffer(**kwargs))

        self.buffers = buffers

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

    @classmethod
    def merge_overall(cls, new_buffers: list[Buffer]) -> list[Buffer]:
        merge_buffers = []
        command_list = [""] * 100
        for buffer in new_buffers:
            if buffer.command == "W":
                command_list[buffer.lba] = buffer.command
            elif buffer.command == "E":
                for each_lba in range(buffer.lba, buffer.lba + buffer.range):
                    command_list[each_lba] = buffer.command

        for buffer in new_buffers:
            if buffer.command == "W" and command_list[buffer.lba] == buffer.command:
                merge_buffers.append(buffer)
            elif buffer.command == "E":
                valid_command_check = True
                for each_lba in range(buffer.lba, buffer.lba + buffer.range):
                    if command_list[each_lba] != buffer.command:
                        valid_command_check = False
                        break
                if valid_command_check:
                    merge_buffers.append(buffer)
        return merge_buffers
