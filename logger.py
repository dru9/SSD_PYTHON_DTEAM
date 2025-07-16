import inspect
import os
from datetime import datetime
from typing import Optional, Tuple
import glob

from constant import (
    LOG_FILE_MAX_SIZE,
    LOG_FILE_NAME,
    LOG_METHOD_NAME_WIDTH,
    PAST_LOG_FILE_FORMAT
)


class Logger:

    def __init__(self, log_dir: str = "./log"):
        self.log_dir = log_dir
        self.latest_log = os.path.join(log_dir, LOG_FILE_NAME)

        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)

        if not os.path.exists(self.latest_log):
            with open(self.latest_log, "w"):
                pass

    def _get_timestamp(self) -> Tuple[str, datetime]:
        now = datetime.now()
        return now.strftime("%y.%m.%d %H:%M"), now

    def _format_log(self, fn_name: str, message: str) -> str:
        timestamp_str, _ = self._get_timestamp()
        fn_name_padded = fn_name.ljust(LOG_METHOD_NAME_WIDTH)
        return f"[{timestamp_str}] {fn_name_padded}: {message}\n"

    def _rollover_if_needed(self) -> None:
        if os.path.getsize(self.latest_log) > LOG_FILE_MAX_SIZE:
            _, now = self._get_timestamp()
            new_name = now.strftime(PAST_LOG_FILE_FORMAT)
            new_path = os.path.join(self.log_dir, new_name)
            os.rename(self.latest_log, new_path)
            with open(self.latest_log, "w"):
                pass

            self._rename_log_files([new_name, "latest.log"])


    def _rename_log_files(self, exclude_files):
        log_files = glob.glob(os.path.join(self.log_dir, "*.log"))
        exclude_files_set = set(exclude_files)
        for log_file in log_files:
            if os.path.basename(log_file) not in exclude_files_set:
                new_name = log_file.replace(".log", ".zip")
                os.rename(log_file, new_name)
                print(f"Renamed {log_file} to {new_name}")

    def print(self, message: str, fn_name: Optional[str] = None) -> None:
        self._rollover_if_needed()
        if fn_name is None:
            frame = inspect.currentframe().f_back
            instance = frame.f_locals.get("self") or frame.f_locals.get("cls")
            class_name = instance.__name__ if instance else None
            method_name = frame.f_code.co_name
            fn_name = f"{class_name}.{method_name}()"

        log_line = self._format_log(fn_name, message)
        with open(self.latest_log, "a", encoding="utf-8") as f:
            f.write(log_line)
