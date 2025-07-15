import subprocess
from abc import ABC, abstractmethod
from typing import List


class ProcessExecutor:
    @staticmethod
    def run(executable: str, args: List[str]) -> bool:
        try:
            result = subprocess.run(
                [executable] + args,
                text=True
            )
            return result.returncode == 0
        except Exception:
            return False


class ShellCommand(ABC):
    def __init__(self, ssd_path: str):
        self.ssd_path = ssd_path
        self.executor = ProcessExecutor()

    @abstractmethod
    def execute(self) -> bool:
        pass


class ReadShellCommand(ShellCommand):
    def __init__(self, ssd_path: str, lba: int):
        super().__init__(ssd_path)
        self.lba = lba

    def execute(self) -> bool:
        return self.executor.run('python', [self.ssd_path, 'R', str(self.lba)])


class WriteShellCommand(ShellCommand):
    def __init__(self, ssd_path: str, lba: int, value: str):
        super().__init__(ssd_path)
        self.lba = lba
        self.value = value

    def execute(self) -> bool:
        return self.executor.run('python', [self.ssd_path, 'W', str(self.lba), self.value])
