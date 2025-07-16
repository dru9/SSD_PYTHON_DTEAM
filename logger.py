import os
from datetime import datetime
from constant import LOG_FILE_MAX_SIZE, LOG_FILE_NAME, PAST_LOG_FILE_FORMAT, LOG_METHOD_NAME_WIDTH


class Logger:
    def __init__(self, log_dir="."):
        self.log_dir = log_dir
        self.latest_log = os.path.join(log_dir, LOG_FILE_NAME)
        if not os.path.exists(self.latest_log):
            with open(self.latest_log, "w"):
                pass

    def _get_timestamp(self):
        now = datetime.now()
        return now.strftime("%y.%m.%d %H:%M"), now

    def _format_log(self, method_name, message):
        timestamp_str, _ = self._get_timestamp()
        method_name_padded = method_name.ljust(LOG_METHOD_NAME_WIDTH)
        return f"[{timestamp_str}] {method_name_padded}: {message}\n"

    def _rollover_if_needed(self):
        if os.path.getsize(self.latest_log) > LOG_FILE_MAX_SIZE:
            _, now = self._get_timestamp()
            new_name = now.strftime(PAST_LOG_FILE_FORMAT)
            new_path = os.path.join(self.log_dir, new_name)
            os.rename(self.latest_log, new_path)

            with open(self.latest_log, "w"):
                pass

    def print(self, method_name, message):
        self._rollover_if_needed()
        log_line = self._format_log(method_name, message)
        with open(self.latest_log, "a", encoding="utf-8") as f:
            f.write(log_line)
