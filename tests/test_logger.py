import pytest
from unittest.mock import patch, mock_open
from logger import Logger
from datetime import datetime

@pytest.fixture
def fixed_datetime():
    return "24.07.16 12:34", datetime(2024, 7, 16, 12, 34, 56)


def test_logger_init_creates_log_file():
    with patch("os.path.exists", return_value=False), patch("builtins.open", mock_open()) as m_open:
        Logger(log_dir=".")
        m_open.assert_called_once_with(".\\latest.log", "w")


def test_format_log_output(fixed_datetime):
    logger = Logger(log_dir=".")
    with patch.object(Logger, "_get_timestamp", return_value=(fixed_datetime[0], fixed_datetime[1])):
        result = logger._format_log("Shell.run", "hello")
        assert result == "[24.07.16 12:34] Shell.run           : hello\n"


def test_print_writes_log_line(fixed_datetime):
    logger = Logger(log_dir=".")
    mock_file = mock_open()

    with patch("os.path.getsize", return_value=0), \
         patch.object(Logger, "_get_timestamp", return_value=(fixed_datetime[0], fixed_datetime[1])), \
         patch("builtins.open", mock_file):

        logger.print("Shell.run", "hello")

        expected_line = "[24.07.16 12:34] Shell.run           : hello\n"
        mock_file().write.assert_called_once_with(expected_line)


def test_rollover_happens_when_log_exceeds_size(fixed_datetime):
    logger = Logger(log_dir=".")

    with patch("os.path.getsize", return_value=Logger.MAX_SIZE + 1), \
         patch.object(Logger, "_get_timestamp", return_value=(fixed_datetime[0], fixed_datetime[1])), \
         patch("os.rename") as mock_rename, \
         patch("builtins.open", mock_open()):

        logger._rollover_if_needed()

        expected_new_log = ".\\until_240716_12h_34m_56s.log"
        mock_rename.assert_called_once_with(".\\latest.log", expected_new_log)


def test_rollover_not_triggered_below_max_size():
    logger = Logger(log_dir=".")

    with patch("os.path.getsize", return_value=Logger.MAX_SIZE - 100), \
         patch("os.rename") as mock_rename:

        logger._rollover_if_needed()
        mock_rename.assert_not_called()
