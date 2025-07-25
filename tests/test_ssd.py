from unittest.mock import mock_open, patch, call

import pytest

from buffer_manager import Buffer, BufferManager
from constant import FILENAME_OUT
from ssd import SSD, FileManager


@pytest.fixture
def ssd(mocker):
    ssd = SSD()
    ssd.file_manager = mocker.Mock()
    return ssd


def test_write_and_read(ssd):
    lba = 0
    expected = "0x12345678"
    ssd.write(lba, expected)
    ssd.read(lba)

    ssd.file_manager.read_nand.assert_called_once()
    ssd.file_manager.write_nand.assert_called_once()
    ssd.file_manager.write_output.assert_called()


def test_read_ssd_nand_txt_file_called_by_read(ssd):
    lba = 0
    ssd.read(lba)

    ssd.file_manager.read_nand.assert_called_once()
    ssd.file_manager.write_output.assert_called_once()


def test_read_ssd_nand_txt_file_called_by_write(ssd):
    lba = 0
    write_contents = "0x00001111"
    ssd.write(lba, write_contents)

    ssd.file_manager.write_nand.assert_called()


def test_read_method_record_ssd_output_txt(ssd):
    lba = 0
    ssd.read(lba)

    ssd.file_manager.read_nand.assert_called()
    ssd.file_manager.write_output.assert_called()


def test_write_ssd(ssd):
    lba = 3
    ssd.write(lba, "0xFFFFFFFF")
    ssd.file_manager.write_nand.assert_called()


def test_write_check_file(ssd):
    lba = 11
    ssd.write(lba, "0x1298CDEF")
    ssd.file_manager.write_nand.assert_called()


def test_execute_command_when_write_normal_should_write_value():
    ssd = SSD()
    commands = [
        [None, "W", "1", "0xAAAAAAAA"]
    ]
    initial_buffers = []
    initial_file_data = '0\t0x11111111\n1\t0x22222222\n2\t0x33333333\n3\t0x33333333\n4\t0x33333333\n5\t0x33333333\n6\t0x33333333\n'
    expected = '0\t0x11111111\n1\t0x22222222\n2\t0x33333333\n3\t0x33333333\n4\t0x33333333\n5\t0x33333333\n6\t0x33333333\n'

    with (patch.object(BufferManager, 'get_buffer', return_value=initial_buffers) as mock_get_buffer, \
          patch('builtins.open', mock_open(read_data=initial_file_data)) as mock_file, \
          patch.object(BufferManager, 'set_buffer') as mock_set_buffer, \
          patch.object(FileManager, 'write_output') as mock_write_buffer):
        ssd.run(commands[0])
        mock_write_buffer.assert_called_once_with("")


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
    ssd = SSD()
    with patch('builtins.open', mock_open()) as mocked_open:
        ssd.run(args)
        mocked_open.assert_called_once_with(FILENAME_OUT, expected_call)
        mocked_open().write.assert_called_once_with(expected_write)


@patch('builtins.open', new_callable=mock_open)
def test_filemanager_nand_write(mock_file):
    lba = 11
    return_value = {lba: "0x00000000"}
    with patch.object(FileManager, '_read_whole_lines', return_value=return_value):
        file_manager = FileManager()
        contents = "0x12341234"
        file_manager.write_nand(lba, contents)
        mock_file.assert_called_with('ssd_nand.txt', 'w')


@patch('builtins.open', new_callable=mock_open)
def test_filemanager_nand_write_fail(mock_file):
    lba = 11
    return_value = {lba: ""}
    with patch.object(FileManager, '_read_whole_lines', return_value=return_value):
        file_manager = FileManager()
        contents = "0x12341234"
        result = file_manager.write_nand(lba, contents)
        assert result == False


@patch('builtins.open', new_callable=mock_open)
def test_filemanager_write_file(mock_file):
    lba = 11
    file_manager = FileManager()
    result = file_manager.write_output("ERROR")
    mock_file.assert_called_with('ssd_output.txt', 'w')


def test_execute_command_when_erase_size_is_out_of_range_should_write_error():
    run_execute_command_and_assert([None, "E", "-1"], 'w', 'ERROR')
    run_execute_command_and_assert([None, "E", "0", "11"], 'w', 'ERROR')
    run_execute_command_and_assert([None, "E", "0", "0"], 'w', 'ERROR')
    run_execute_command_and_assert([None, "E", "98", "5"], 'w', 'ERROR')
    run_execute_command_and_assert([None, "E", "STR"], 'w', 'ERROR')
    run_execute_command_and_assert([None, "E", "0", "HAHA"], 'w', 'ERROR')


def test_read_from_buffer_when_lba_is_cached():
    ssd = SSD()
    commands = [
        [None, "R", "50"]
    ]
    initial_buffers = [Buffer(command="W", lba=50, data="0xAAAABBBB", range=""),
                       Buffer(command="W", lba=50, data="0x12345678", range=""),
                       Buffer(command="W", lba=20, data="0xABABCCCC", range="")]
    expected_write = "0x12345678"
    with (patch.object(BufferManager, 'get_buffer', return_value=initial_buffers),
          patch('builtins.open', mock_open()) as mocked_open, \
          patch.object(BufferManager, 'set_buffer') as mock_set_buffer):
        ssd.run(commands[0])

        mock_set_buffer.assert_not_called()
        mocked_open().read.assert_not_called()
        mocked_open().write.assert_called_once_with(expected_write)


def test_read_buffer_commands_when_not_exists():
    ssd = SSD()
    commands = [
        [None, "R", "12"]
    ]
    initial_buffers = [Buffer(command="W", lba=20, data="0xABCDABCD", range=""),
                       Buffer(command="E", lba=10, data="", range=4)]
    expected_write = "0x00000000"

    with (patch.object(BufferManager, 'get_buffer', return_value=initial_buffers),
          patch('builtins.open', mock_open()) as mocked_open, \
          patch.object(BufferManager, 'set_buffer') as mock_set_buffer):
        ssd.run(commands[0])

        mock_set_buffer.assert_not_called()
        mocked_open().write.assert_called_once_with(expected_write)


def execute_commands_check_buffer_with_expected_buffers(commands, expectd_buffers_for_all_commands, initial_buffers):
    ssd = SSD()
    with (patch.object(BufferManager, 'get_buffer', return_value=initial_buffers),
          patch('builtins.open', mock_open()) as mocked_open, \
          patch.object(BufferManager, 'set_buffer') as mock_set_buffer):
        for command, expected_buffers in zip(commands, expectd_buffers_for_all_commands):
            ssd.run(command)

            args, kwargs = mock_set_buffer.call_args
            buffers = args[0]
            assert len(buffers) == len(expected_buffers)

            for buffer, expected in zip(buffers, expected_buffers):
                assert buffer.command == expected["command"]
                assert buffer.lba == expected["lba"]
                assert str(buffer.data if expected["command"] == "W" else buffer.range) == str(
                    expected["data_or_range"])


def test_buffer_overwrites_earlier_instructions_with_last_for_same_lba():
    commands = [
        [None, "W", "20", "0xABCDABCD"],
        [None, "W", "20", "0x12341234"],
        [None, "E", "20", "1"]
    ]
    initial_buffers = []
    expectd_buffers_for_all_commands = [
        [{'command': 'W', 'lba': 20, 'data_or_range': "0xABCDABCD"}],
        [{'command': 'W', 'lba': 20, 'data_or_range': "0x12341234"}],
        [{'command': 'E', 'lba': 20, 'data_or_range': 1}]
    ]

    execute_commands_check_buffer_with_expected_buffers(commands, expectd_buffers_for_all_commands, initial_buffers)


def test_merge_buffer_commands_when_possible():
    commands = [
        [None, "E", "12", "3"]
    ]
    initial_buffers = [Buffer(command="W", lba=20, data="0xABCDABCD", range=""),
                       Buffer(command="E", lba=10, data="", range=4)]
    expectd_buffers_for_all_commands = [
        [
            {"command": "W", "lba": 20, "data_or_range": "0xABCDABCD"},
            {"command": "E", "lba": 10, "data_or_range": 5}
        ]
    ]

    execute_commands_check_buffer_with_expected_buffers(commands, expectd_buffers_for_all_commands, initial_buffers)


def test_buffer_commands_write_when_possible():
    commands = [
        [None, "W", "12", "0x0000AAAA"]
    ]
    initial_buffers = []
    expectd_buffers_for_all_commands = [
        [
            {"command": "W", "lba": 12, "data_or_range": "0x0000AAAA"}
        ]
    ]

    execute_commands_check_buffer_with_expected_buffers(commands, expectd_buffers_for_all_commands, initial_buffers)


def test_merge_buffer_commands_when_not_same_index():
    commands = [
        [None, "W", "12", "0xAAAABBBB"]
    ]
    initial_buffers = [Buffer(command="W", lba=20, data="0xABCDABCD", range="")]
    expectd_buffers_for_all_commands = [
        [
            {"command": "W", "lba": 20, "data_or_range": "0xABCDABCD"},
            {"command": "W", "lba": 12, "data_or_range": "0xAAAABBBB"},
        ]
    ]

    execute_commands_check_buffer_with_expected_buffers(commands, expectd_buffers_for_all_commands, initial_buffers)


def test_merge_buffer_commands_when_same_index():
    commands = [
        [None, "W", "12", "0xAAAABBBB"]
    ]
    initial_buffers = [Buffer(command="W", lba=12, data="0xABCDABCD", range=""),
                       Buffer(command="W", lba=22, data="0xABCDABCD", range="")]
    expectd_buffers_for_all_commands = [
        [
            {"command": "W", "lba": 22, "data_or_range": "0xABCDABCD"},
            {"command": "W", "lba": 12, "data_or_range": "0xAAAABBBB"},
        ]
    ]
    execute_commands_check_buffer_with_expected_buffers(commands, expectd_buffers_for_all_commands, initial_buffers)

def test_merge_buffer_commands_when_same_index_with_erase_range_1():
    commands = [
        [None, "W", "12", "0xAAAABBBB"]
    ]
    initial_buffers = [Buffer(command="E", lba=12, data="", range=1),
                       Buffer(command="W", lba=22, data="0xABCDABCD", range="")]
    expectd_buffers_for_all_commands = [
        [
            {"command": "W", "lba": 22, "data_or_range": "0xABCDABCD"},
            {"command": "W", "lba": 12, "data_or_range": "0xAAAABBBB"},
        ]
    ]
    execute_commands_check_buffer_with_expected_buffers(commands, expectd_buffers_for_all_commands, initial_buffers)

def test_merge_buffer_commands_when_erase_range_2():
    commands = [
        [None, "W", "12", "0xAAAABBBB"]
    ]
    initial_buffers = [Buffer(command="E", lba=12, data="", range=2),
                       Buffer(command="W", lba=22, data="0xABCDABCD", range="")]
    expectd_buffers_for_all_commands = [
        [
            {"command": "E", "lba": 13, "data_or_range": "1"},
            {"command": "W", "lba": 22, "data_or_range": "0xABCDABCD"},
            {"command": "W", "lba": 12, "data_or_range": "0xAAAABBBB"}
        ]
    ]
    execute_commands_check_buffer_with_expected_buffers(commands, expectd_buffers_for_all_commands, initial_buffers)


def test_flush_buffer_when_mode_is_flush_should_execute_instruction():
    ssd = SSD()
    commands = [
        [None, "F"]
    ]
    initial_buffers = [Buffer(command="W", lba=2, data="0xABCDABCD", range="")]
    initial_file_data = '0\t0x11111111\n1\t0x22222222\n2\t0x33333333\n3\t0x33333333\n'
    expected = '0\t0x11111111\n1\t0x22222222\n2\t0xABCDABCD\n3\t0x33333333\n'
    expected_lines = expected.splitlines(keepends=True)

    with (patch.object(BufferManager, 'get_buffer', return_value=initial_buffers) as mock_get_buffer, \
          patch('builtins.open', mock_open(read_data=initial_file_data)) as mock_file, \
          patch.object(BufferManager, 'set_buffer') as mock_set_buffer, \
          patch.object(FileManager, 'write_output') as mock_write_output):
        ssd.run(commands[0])

        args, kwargs = mock_set_buffer.call_args
        written_buffers = args[0]
        assert len(written_buffers) == 0
        write_calls = mock_file().write.call_args_list
        expected_calls = [call(line) for line in expected_lines]
        assert write_calls == expected_calls


def test_flush_buffer_when_buffers_are_full_should_execute_instruction():
    ssd = SSD()
    commands = [
        [None, "W", "2", "0x12345678"]
    ]
    initial_buffers = [Buffer(command="W", lba=2, data="0xABCDABCD", range=""),
                       Buffer(command="W", lba=3, data="0xABCDABCD", range=""),
                       Buffer(command="W", lba=4, data="0xABCDABCD", range=""),
                       Buffer(command="W", lba=5, data="0xABCDABCD", range=""),
                       Buffer(command="W", lba=6, data="0xABCDABCD", range="")]
    initial_file_data = '0\t0x11111111\n1\t0x22222222\n2\t0x33333333\n3\t0x33333333\n4\t0x33333333\n5\t0x33333333\n6\t0x33333333\n'
    expected = '0\t0x11111111\n1\t0x22222222\n2\t0xABCDABCD\n3\t0x33333333\n4\t0x33333333\n5\t0x33333333\n6\t0x33333333\n'
    expected += '0\t0x11111111\n1\t0x22222222\n2\t0x33333333\n3\t0xABCDABCD\n4\t0x33333333\n5\t0x33333333\n6\t0x33333333\n'
    expected += '0\t0x11111111\n1\t0x22222222\n2\t0x33333333\n3\t0x33333333\n4\t0xABCDABCD\n5\t0x33333333\n6\t0x33333333\n'
    expected += '0\t0x11111111\n1\t0x22222222\n2\t0x33333333\n3\t0x33333333\n4\t0x33333333\n5\t0xABCDABCD\n6\t0x33333333\n'
    expected += '0\t0x11111111\n1\t0x22222222\n2\t0x33333333\n3\t0x33333333\n4\t0x33333333\n5\t0x33333333\n6\t0xABCDABCD\n'
    expected_lines = expected.splitlines(keepends=True)

    with (patch.object(BufferManager, 'get_buffer', return_value=initial_buffers) as mock_get_buffer, \
          patch('builtins.open', mock_open(read_data=initial_file_data)) as mock_file, \
          patch.object(BufferManager, 'set_buffer') as mock_set_buffer, \
          patch.object(FileManager, 'write_output')):
        ssd.run(commands[0])

        write_calls = mock_file().write.call_args_list
        expected_calls = [call(line) for line in expected_lines]
        assert write_calls == expected_calls


def test_flush_buffer_should_write_empty_string_when_normal():
    ssd = SSD()
    commands = [
        [None, "F"]
    ]
    initial_buffers = []
    initial_file_data = '0\t0x11111111\n1\t0x22222222\n2\t0x33333333\n3\t0x33333333\n4\t0x33333333\n5\t0x33333333\n6\t0x33333333\n'
    expected = '0\t0x11111111\n1\t0x22222222\n2\t0x33333333\n3\t0x33333333\n4\t0x33333333\n5\t0x33333333\n6\t0x33333333\n'

    with (patch.object(BufferManager, 'get_buffer', return_value=initial_buffers) as mock_get_buffer, \
          patch('builtins.open', mock_open(read_data=initial_file_data)) as mock_file, \
          patch.object(BufferManager, 'set_buffer') as mock_set_buffer, \
          patch.object(FileManager, 'write_output') as mock_write_buffer):
        ssd.run(commands[0])
        mock_write_buffer.assert_called_once_with("")


def test_command_buffer_test_erase_keep_buffer():
    ssd = SSD()
    commands = [
        [None, "E", "88", 6]
    ]
    initial_buffers = [
        Buffer(command="E", lba=93, data="", range=7),
    ]
    with (patch.object(BufferManager, 'get_buffer', return_value=initial_buffers),
          patch('builtins.open', mock_open()) as mocked_open, \
          patch.object(BufferManager, 'set_buffer') as mock_set_buffer):
        ssd.run(commands[0])

        args, kwargs = mock_set_buffer.call_args
        buffer_written1 = args[0][0]
        assert buffer_written1.command == "E"
        assert buffer_written1.lba == 93
        assert buffer_written1.range == 7
        assert len(args[0]) == 2
        buffer_written1 = args[0][1]
        assert buffer_written1.command == "E"
        assert buffer_written1.lba == 88
        assert buffer_written1.range == 6


def test_command_buffer_test_erase_overlap_range():
    ssd = SSD()
    commands = [
        [None, "E", "10", 3]
    ]
    initial_buffers = [
        Buffer(command="E", lba=12, data="", range=2),
    ]

    with (patch.object(BufferManager, 'get_buffer', return_value=initial_buffers),
          patch('builtins.open', mock_open()) as mocked_open, \
          patch.object(BufferManager, 'set_buffer') as mock_set_buffer):
        ssd.run(commands[0])

        args, kwargs = mock_set_buffer.call_args
        buffer_written = args[0][0]
        assert buffer_written.command == "E"
        assert buffer_written.lba == 10
        assert buffer_written.data == ""
        assert buffer_written.range == 4

        assert len(args[0]) == 1


def test_command_buffer_test_erase_same_range_1():
    ssd = SSD()
    commands = [
        [None, "E", "15", 5]
    ]
    initial_buffers = [
        Buffer(command="E", lba=15, data="", range=5),
    ]

    with (patch.object(BufferManager, 'get_buffer', return_value=initial_buffers),
          patch('builtins.open', mock_open()) as mocked_open, \
          patch.object(BufferManager, 'set_buffer') as mock_set_buffer):
        ssd.run(commands[0])

        args, kwargs = mock_set_buffer.call_args
        buffer_written = args[0][0]
        assert buffer_written.command == "E"
        assert buffer_written.lba == 15
        assert buffer_written.data == ""
        assert buffer_written.range == 5

        assert len(args[0]) == 1


def test_command_buffer_test_erase_same_range_2():
    ssd = SSD()
    commands = [
        [None, "E", "50", 6]
    ]
    initial_buffers = [
        Buffer(command="E", lba=50, data="", range=6),
    ]

    with (patch.object(BufferManager, 'get_buffer', return_value=initial_buffers),
          patch('builtins.open', mock_open()) as mocked_open, \
          patch.object(BufferManager, 'set_buffer') as mock_set_buffer):
        ssd.run(commands[0])

        args, kwargs = mock_set_buffer.call_args
        buffer_written1 = args[0][0]
        assert buffer_written1.command == "E"
        assert buffer_written1.lba == 50
        assert buffer_written1.range == 6
        assert len(args[0]) == 1


def test_command_buffer_test_erase_over10():
    ssd = SSD()
    commands = [
        [None, "E", "22", 4]
    ]
    initial_buffers = [
        Buffer(command="E", lba=16, data="", range=9),
    ]

    with (patch.object(BufferManager, 'get_buffer', return_value=initial_buffers),
          patch('builtins.open', mock_open()) as mocked_open, \
          patch.object(BufferManager, 'set_buffer') as mock_set_buffer):
        ssd.run(commands[0])

        args, kwargs = mock_set_buffer.call_args
        buffer_written1 = args[0][0]
        assert buffer_written1.command == "E"
        assert buffer_written1.lba == 16
        assert buffer_written1.range == 10
        assert len(args[0]) == 1


def test_erase_command_expands_buffer_range_by_merging():
    ssd = SSD()
    commands = [
        [None, "E", "95", 5]
    ]
    initial_buffers = [
        Buffer(command="E", lba=93, data="", range=7),
    ]

    with (patch.object(BufferManager, 'get_buffer', return_value=initial_buffers),
          patch('builtins.open', mock_open()) as mocked_open, \
          patch.object(BufferManager, 'set_buffer') as mock_set_buffer):
        ssd.run(commands[0])
        args, kwargs = mock_set_buffer.call_args
        buffer_written1 = args[0][0]
        assert buffer_written1.command == "E"
        assert buffer_written1.lba == 93
        assert buffer_written1.range == 7
        assert len(args[0]) == 1


def test_command_buffer_erase_larger_new_range():
    ssd = SSD()
    commands = [
        [None, "E", "50", 7]
    ]
    initial_buffers = [
        Buffer(command="E", lba=52, data="", range=2),
    ]

    with (patch.object(BufferManager, 'get_buffer', return_value=initial_buffers),
          patch('builtins.open', mock_open()) as mocked_open, \
          patch.object(BufferManager, 'set_buffer') as mock_set_buffer):
        ssd.run(commands[0])

        args, kwargs = mock_set_buffer.call_args
        buffer_written1 = args[0][0]
        assert buffer_written1.command == "E"
        assert buffer_written1.lba == 50
        assert buffer_written1.range == 7
        assert len(args[0]) == 1


def test_execute_command_when_flush_command_invalid_should_write_error():
    run_execute_command_and_assert([None, "F", "0"], 'w', 'ERROR')


def test_merge_erase_buffer():
    commands = [
        [None, "E", "20", "2"],
        [None, "E", "21", "2"],
    ]
    expected = [
        [None, "E", "20", "3"],
    ]
    execute_command_and_test_buffer_with_expected(commands, expected, False)


def test_merge_erase_buffer_hard():
    commands = [
        [None, "E", "20", "1"],
        [None, "E", "21", "2"],
    ]
    expected = [
        [None, "E", "20", "3"],
    ]
    execute_command_and_test_buffer_with_expected(commands, expected, False)


def test_remove_erase_buffer():
    commands = [
        [None, "E", "20", "3"],
        [None, "W", "20", "0xABCDABC0"],
        [None, "W", "21", "0xABCDABC0"],
        [None, "W", "22", "0xABCDABC0"],
    ]
    expected = [
        [None, "W", "20", "0xABCDABC0"],
        [None, "W", "21", "0xABCDABC0"],
        [None, "W", "22", "0xABCDABC0"],
    ]
    execute_command_and_test_buffer_with_expected(commands, expected)


def test_remove_erase_buffer_hard():
    commands = [
        [None, "E", "20", "3"],
        [None, "W", "21", "0xABCDABC0"],
        [None, "W", "20", "0xABCDABC0"],
        [None, "W", "22", "0xABCDABC0"],
    ]
    expected = [
        [None, "W", "21", "0xABCDABC0"],
        [None, "W", "20", "0xABCDABC0"],
        [None, "W", "22", "0xABCDABC0"],
    ]
    execute_command_and_test_buffer_with_expected(commands, expected)


def execute_command_and_test_buffer_with_expected(commands, expected, data_flag=True):
    ssd = SSD()
    ssd.buffer_manager.set_buffer([])
    for command in commands:
        ssd.run(command)
    buffers = ssd.buffer_manager.get_buffer()
    assert len(expected) == len(buffers)
    for gt, buffer_written in zip(expected, buffers):
        assert str(buffer_written.command) == gt[1]
        assert str(buffer_written.lba) == gt[2]
        if data_flag:
            assert str(buffer_written.data) == gt[3]
        else:
            assert str(buffer_written.range) == gt[3]
