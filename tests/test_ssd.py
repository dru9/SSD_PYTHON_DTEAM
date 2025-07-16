from unittest.mock import mock_open, patch, call

import pytest

from command_buffer import BufferManager, Buffer
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


@pytest.mark.skip
def test_execute_command_when_write_normal_should_write_value():
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


def test_execute_command_when_args_is_invalid_should_write_error():
    run_execute_command_and_assert([None, "W"], 'w', 'ERROR')
    run_execute_command_and_assert([None], 'w', 'ERROR')


def test_execute_command_when_read_out_of_range_should_write_error():
    run_execute_command_and_assert([None, "R", "100"], 'w', 'ERROR')
    run_execute_command_and_assert([None, "R", "-1"], 'w', 'ERROR')


def test_execute_command_when_write_invalid_value_should_write_error():
    run_execute_command_and_assert([None, "W", "100", "0x00000000"], 'w', 'ERROR')
    run_execute_command_and_assert([None, "W", "0", "0xAAAAAAAQ"], 'w', 'ERROR')
    run_execute_command_and_assert([None, "W", "0", "12AAAAAAAQ"], 'w', 'ERROR')
    run_execute_command_and_assert([None, "W", "0", "0x12345678910"], 'w', 'ERROR')


def test_execute_command_when_command_invalid_should_write_error():
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


@pytest.mark.skip
def test_erase_replace_value_as_zero():
    ssd = SSD(FileManager())
    initial_file_data = '0\t0x11111111\n1\t0x22222222\n2\t0x33333333\n'
    expected = '0\t0x11111111\n1\t0x00000000\n2\t0x00000000\n'
    expected_lines = expected.splitlines(keepends=True)

    mock_file = mock_open(read_data=initial_file_data)

    with patch('builtins.open', mock_file), patch.object(FileManager, 'write_output_txt'):
        args = [None, "E", "1", "2"]
        ssd.execute_command(args)

        write_calls = mock_file().write.call_args_list

        expected_calls = [call(line) for line in expected_lines]
        assert write_calls == expected_calls


def test_execute_command_when_erase_size_is_out_of_range_should_write_error():
    run_execute_command_and_assert([None, "E", "-1"], 'w', 'ERROR')
    run_execute_command_and_assert([None, "E", "0", "11"], 'w', 'ERROR')
    run_execute_command_and_assert([None, "E", "0", "0"], 'w', 'ERROR')
    run_execute_command_and_assert([None, "E", "98", "5"], 'w', 'ERROR')
    run_execute_command_and_assert([None, "E", "STR"], 'w', 'ERROR')
    run_execute_command_and_assert([None, "E", "0", "HAHA"], 'w', 'ERROR')


def test_buffer_overwrites_earlier_instructions_with_last_for_same_lba():
    ssd = SSD(FileManager())
    commands = [
        [None, "W", "20", "0xABCDABCD"],
        [None, "W", "20", "0x12341234"],
        [None, "E", "20", "1"]
    ]
    initial_buffers = []
    with patch.object(BufferManager, 'get_buffer', return_value=initial_buffers), patch('builtins.open', mock_open()), \
            patch.object(BufferManager, 'set_buffer') as mock_set_buffer:
        ssd.execute_command(commands[0])

        args, kwargs = mock_set_buffer.call_args
        buffer_written = args[0][0]
        assert buffer_written.command == "W"
        assert buffer_written.lba == 20
        assert buffer_written.data == "0xABCDABCD"

        ssd.execute_command(commands[1])
        args, kwargs = mock_set_buffer.call_args
        buffer_written = args[0][0]
        assert buffer_written.command == "W"
        assert buffer_written.lba == 20
        assert buffer_written.data == "0x12341234"

        ssd.execute_command(commands[2])
        args, kwargs = mock_set_buffer.call_args
        buffer_written = args[0][0]
        assert buffer_written.command == "E"
        assert buffer_written.lba == 20
        assert buffer_written.range == 1


def test_read_from_buffer_when_lba_is_cached():
    ssd = SSD(FileManager())
    commands = [
        [None, "R", "50"]
    ]
    initial_buffers = [Buffer(command="W", lba=50, data="0xAAAABBBB", range=""), Buffer(command="W", lba=20, data="0xABABCCCC", range="")]
    expected_write = "0xAAAABBBB"
    with patch.object(BufferManager, 'get_buffer', return_value=initial_buffers), patch('builtins.open', mock_open()) as mocked_open, \
            patch.object(BufferManager, 'set_buffer') as mock_set_buffer:
        ssd.execute_command(commands[0])

        mock_set_buffer.assert_not_called()
        mocked_open().write.assert_called_once_with(expected_write)

def test_merge_buffer_commands_when_possible():
    ssd = SSD(FileManager())
    commands = [
        [None, "E", "12", "3"]
    ]
    initial_buffers = [Buffer(command="W", lba=20, data="0xABCDABCD", range=""),
                       Buffer(command="E", lba=10, data="", range=4)]

    with patch.object(BufferManager, 'get_buffer', return_value=initial_buffers), patch('builtins.open',
                                                                                        mock_open()) as mocked_open, \
            patch.object(BufferManager, 'set_buffer') as mock_set_buffer:
        ssd.execute_command(commands[0])

        args, kwargs = mock_set_buffer.call_args
        buffer_written = args[0][0]
        assert buffer_written.command == "W"
        assert buffer_written.lba == 20
        assert buffer_written.data == "0xABCDABCD"

        buffer_written = args[0][1]
        assert buffer_written.command == "E"
        assert buffer_written.lba == 10
        assert buffer_written.range == 5

        assert len(args[0]) == 2