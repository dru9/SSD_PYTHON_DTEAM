import pytest
from unittest.mock import patch, mock_open
from logger import Logger
from datetime import datetime
from constant import LOG_FILE_MAX_SIZE, LOG_FILE_NAME, LOG_METHOD_NAME_WIDTH


@pytest.fixture
def fixed_datetime():
    return "24.07.16 12:34", datetime(2024, 7, 16, 12, 34, 56)


@pytest.fixture
def logger():
    return Logger(log_dir=".")


@pytest.fixture
def test_case_for_print():
    return {"method_name": "Shell.run",
            "message": "hello",
            "expected_line": f"[24.07.16 12:34] {"Shell.run".ljust(LOG_METHOD_NAME_WIDTH)}: hello\n"}


def test_logger_init_creates_log_file():
    with patch("os.path.exists", return_value=False), patch("builtins.open", mock_open()) as m_open:
        Logger(log_dir=".")
        m_open.assert_called_once_with(f".\\{LOG_FILE_NAME}", "w")


def test_format_log_output(fixed_datetime, logger, test_case_for_print):
    with patch.object(Logger, "_get_timestamp", return_value=(fixed_datetime[0], fixed_datetime[1])):
        result = logger._format_log(test_case_for_print["method_name"], test_case_for_print["message"])
        assert result == test_case_for_print["expected_line"]


def test_print_writes_log_line(fixed_datetime, logger, test_case_for_print):
    mock_file = mock_open()

    with patch("os.path.getsize", return_value=0), \
            patch.object(Logger, "_get_timestamp", return_value=(fixed_datetime[0], fixed_datetime[1])), \
            patch("builtins.open", mock_file):
        logger.print(test_case_for_print["method_name"], test_case_for_print["message"])

        mock_file().write.assert_called_once_with(test_case_for_print["expected_line"])


def test_rollover_happens_when_log_exceeds_size(fixed_datetime, logger):
    with patch("os.path.getsize", return_value=LOG_FILE_MAX_SIZE + 1), \
            patch.object(Logger, "_get_timestamp", return_value=(fixed_datetime[0], fixed_datetime[1])), \
            patch("os.rename") as mock_rename, \
            patch("builtins.open", mock_open()):
        logger._rollover_if_needed()

        expected_new_log = ".\\until_240716_12h_34m_56s.zip"
        mock_rename.assert_called_once_with(f".\\{LOG_FILE_NAME}", expected_new_log)


def test_rollover_not_triggered_below_max_size(logger):
    with patch("os.path.getsize", return_value=LOG_FILE_MAX_SIZE - 100), \
            patch("os.rename") as mock_rename:
        logger._rollover_if_needed()
        mock_rename.assert_not_called()
