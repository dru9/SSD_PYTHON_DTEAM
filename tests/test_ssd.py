from unittest.mock import mock_open, patch, call

import pytest

from constant import FILENAME, FILENAME_OUT
from ssd import SSD, FileManager


@pytest.fixture
def ssd(mocker):
    file_manager = mocker.Mock()
    ssd = SSD(file_manager)
    return ssd


def test_write_and_read(ssd):
    lba = 0
    expected = "0x12345678"
    ssd.write(lba, expected)
    ssd.read(lba)

    ssd.file_manager.read_nand_txt.assert_called_once()
    ssd.file_manager.write_nand_txt.assert_called_once()
    ssd.file_manager.write_output_txt.assert_called()


def test_read_ssd_nand_txt_file_called_by_read(ssd):
    lba = 0
    ssd.read(lba)

    ssd.file_manager.read_nand_txt.assert_called_once()
    ssd.file_manager.write_output_txt.assert_called_once()


def test_read_ssd_nand_txt_file_called_by_write(ssd):
    lba = 0
    write_contents = "0x00001111"
    ssd.write(lba, write_contents)

    ssd.file_manager.write_nand_txt.assert_called()


def test_read_method_record_ssd_output_txt(ssd):
    lba = 0
    ssd.read(lba)

    ssd.file_manager.read_nand_txt.assert_called()
    ssd.file_manager.write_output_txt.assert_called()


def test_write_ssd(ssd):
    lba = 3
    ssd.write(lba, "0xFFFFFFFF")

    ssd.file_manager.write_nand_txt.assert_called()


def test_write_check_file(ssd):
    lba = 11
    ssd.write(lba, "0x1298CDEF")

    ssd.file_manager.write_nand_txt.assert_called()


def test_execute_command_When_write_normal_Should_write_value():
    ssd = SSD(FileManager())
    initial_file_data = '0\t0x11111111\n1\t0x22222222\n2\t0x33333333\n'
    mocked_open = mock_open(read_data=initial_file_data)

    with patch('builtins.open', mocked_open):
        args = [None, "W", "1", "0xAAAAAAAA"]
        ssd.execute_command(args)

        mocked_open.assert_has_calls([call(FILENAME, 'r')], any_order=False)
        mocked_open.assert_has_calls([call(FILENAME, 'w')], any_order=False)
        mocked_open.assert_has_calls([call(FILENAME_OUT, 'w')], any_order=False)

        mocked_open().write.assert_any_call("")


def test_execute_command_When_args_is_invalid_Should_write_error():
    run_execute_command_and_assert([None, "W"], 'w', 'ERROR')
    run_execute_command_and_assert([None], 'w', 'ERROR')


def test_execute_command_When_read_out_of_range_Should_write_error():
    run_execute_command_and_assert([None, "R", "100"], 'w', 'ERROR')
    run_execute_command_and_assert([None, "R", "-1"], 'w', 'ERROR')


def test_execute_command_When_write_invalid_value_Should_write_error():
    run_execute_command_and_assert([None, "W", "100", "0x00000000"], 'w', 'ERROR')
    run_execute_command_and_assert([None, "W", "0", "0xAAAAAAAQ"], 'w', 'ERROR')
    run_execute_command_and_assert([None, "W", "0", "12AAAAAAAQ"], 'w', 'ERROR')
    run_execute_command_and_assert([None, "W", "0", "0x12345678910"], 'w', 'ERROR')


def test_execute_command_When_command_invalid_Should_write_error():
    run_execute_command_and_assert([None, "A", "0"], 'w', 'ERROR')


def run_execute_command_and_assert(args, expected_call, expected_write):
    ssd = SSD(FileManager())
    with patch('builtins.open', mock_open()) as mocked_open:
        ssd.execute_command(args)
        mocked_open.assert_called_once_with(FILENAME_OUT, expected_call)
        mocked_open().write.assert_called_once_with(expected_write)


@patch('builtins.open', new_callable=mock_open)
def test_filemanager_nand_write(mock_file):
    lba = 11
    return_value = {lba: "0x00000000"}
    with patch.object(FileManager, '_read_whole_contents_nand_txt', return_value=return_value):
        file_manager = FileManager()
        contents = "0x12341234"
        file_manager.write_nand_txt(lba, contents)
        mock_file.assert_called_with('ssd_nand.txt', 'w')


@patch('builtins.open', new_callable=mock_open)
def test_filemanager_nand_write_fail(mock_file):
    lba = 11
    return_value = {lba: ""}
    with patch.object(FileManager, '_read_whole_contents_nand_txt', return_value=return_value):
        file_manager = FileManager()
        contents = "0x12341234"
        result = file_manager.write_nand_txt(lba, contents)
        assert result == False


@patch('builtins.open', new_callable=mock_open)
def test_filemanager_write_file(mock_file):
    lba = 11
    file_manager = FileManager()
    result = file_manager.write_output_txt("ERROR")
    mock_file.assert_called_with('ssd_output.txt', 'w')
