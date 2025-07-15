from unittest.mock import mock_open, patch
import pytest
from pytest_mock import MockerFixture
from ssd import SSD, FileManager
from unittest.mock import mock_open, patch, call
from constant import FILENAME, FILENAME_OUT


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

def test_execute_command_When_args_is_invalid_Should_write_error():
    with patch('builtins.open', mock_open()) as mocked_open:
        args = [None, "W"]
        ssd = SSD(FileManager())
        ssd.execute_command(args)
        mocked_open.assert_called_once_with(FILENAME_OUT, 'w')
        mocked_open().write.assert_called_once_with('ERROR')

    mocked_open = mock_open()
    with patch('builtins.open', mocked_open):
        args = [None]
        ssd = SSD(FileManager())
        ssd.execute_command(args)
        mocked_open.assert_called_once_with(FILENAME_OUT, 'w')
        mocked_open().write.assert_called_once_with('ERROR')


def test_execute_command_When_write_normal_Should_write_value():
    initial_file_data = '0\t0x11111111\n1\t0x22222222\n2\t0x33333333\n'
    m = mock_open(read_data=initial_file_data)

    with patch('builtins.open', m):
        args = [None, "W", "1", "0xAAAAAAAA"]
        ssd = SSD(FileManager())
        ssd.execute_command(args)

        m.assert_has_calls([call(FILENAME, 'r')], any_order=False)
        m.assert_has_calls([call(FILENAME, 'w')], any_order=False)
        m.assert_has_calls([call(FILENAME_OUT, 'w')], any_order=False)

        m().write.assert_any_call("")


def test_execute_command_When_read_out_of_range_Should_write_error():
    mocked_open = mock_open()

    with patch('builtins.open', mocked_open):
        args = [None, "R", "100"]
        ssd = SSD(FileManager())
        ssd.execute_command(args)
        mocked_open.assert_called_once_with(FILENAME_OUT, 'w')
        mocked_open().write.assert_called_once_with('ERROR')

    mocked_open = mock_open()

    with patch('builtins.open', mocked_open):
        args = [None, "R", "-1"]
        ssd = SSD(FileManager())
        ssd.execute_command(args)
        mocked_open.assert_called_once_with(FILENAME_OUT, 'w')
        mocked_open().write.assert_called_once_with('ERROR')

        
def test_execute_command_When_write_invalid_value_Should_write_error():
    mocked_open = mock_open()
    with patch('builtins.open', mocked_open):
        args = [None, "W", "100", "0x00000000"]
        ssd = SSD(FileManager())
        ssd.execute_command(args)
        mocked_open.assert_called_once_with(FILENAME_OUT, 'w')
        mocked_open().write.assert_called_once_with('ERROR')

    mocked_open = mock_open()
    with patch('builtins.open', mocked_open):
        args = [None, "W", "0", "0xAAAAAAAQ"]
        ssd = SSD(FileManager())
        ssd.execute_command(args)
        mocked_open.assert_called_once_with(FILENAME_OUT, 'w')
        mocked_open().write.assert_called_once_with('ERROR')

    mocked_open = mock_open()
    with patch('builtins.open', mocked_open):
        args = [None, "W", "0", "12AAAAAAAQ"]
        ssd = SSD(FileManager())
        ssd.execute_command(args)
        mocked_open.assert_called_once_with(FILENAME_OUT, 'w')
        mocked_open().write.assert_called_once_with('ERROR')

    mocked_open = mock_open()
    with patch('builtins.open', mocked_open):
        args = [None, "W", "0", "0x12345678910"]
        ssd = SSD(FileManager())
        ssd.execute_command(args)
        mocked_open.assert_called_once_with(FILENAME_OUT, 'w')
        mocked_open().write.assert_called_once_with('ERROR')


def test_execute_command_When_command_invalid_Should_write_error():
    mocked_open = mock_open()
    with patch('builtins.open', mocked_open):
        args = [None, "A", "0"]
        ssd = SSD(FileManager())
        ssd.execute_command(args)
        mocked_open.assert_called_once_with(FILENAME_OUT, 'w')
        mocked_open().write.assert_called_once_with('ERROR')
