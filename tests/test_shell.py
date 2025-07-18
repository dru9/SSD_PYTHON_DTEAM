import pytest

from constant import (
    MESSAGE_HELP,
    MESSAGE_PASS,
    ShellCommandEnum,
    SIZE_LBA
)
from shell import Shell


@pytest.fixture
def ssd_py_path(mocker):
    return mocker.patch("shell.FILENAME_MAIN_SSD", new="../ssd.py")


@pytest.fixture
def file_mock(mocker):
    return mocker.patch('builtins.open', mocker.mock_open(read_data=''))


@pytest.fixture
def shell_mock(mocker):
    pat = mocker.patch('commands.subprocess.run')
    mock_result = mocker.Mock(returncode=0)
    pat.return_value = mock_result
    return pat


def test_read_mock(file_mock, shell_mock):
    Shell.execute_command(cmd=ShellCommandEnum.READ, args=[0])
    shell_mock.assert_called_once_with(['python', 'ssd.py', 'R', '0'], text=True)
    file_mock.assert_any_call('ssd_output.txt', 'r')


def test_write_mock(file_mock, shell_mock):
    Shell.execute_command(cmd=ShellCommandEnum.WRITE, args=[3, "0x00000003"])
    shell_mock.assert_called_once_with(['python', 'ssd.py', 'W', '3', "0x00000003"], text=True)
    file_mock.assert_any_call('ssd_output.txt', 'r')


def test_full_read_mock(file_mock, shell_mock):
    Shell.execute_command(cmd=ShellCommandEnum.FULLREAD, args=[])
    shell_mock.assert_called_with(['python', 'ssd.py', 'R', '99'], text=True)
    file_mock.assert_any_call('ssd_output.txt', 'r')


def test_full_write_mock(file_mock, shell_mock):
    Shell.execute_command(cmd=ShellCommandEnum.FULLWRITE, args=["0x00000003"])
    shell_mock.assert_called_with(['python', 'ssd.py', 'W', '99', "0x00000003"], text=True)
    file_mock.assert_any_call('ssd_output.txt', 'r')


def test_erase_mock(file_mock, shell_mock):
    ret = Shell.execute_command(cmd=ShellCommandEnum.ERASE, args=[0, 5])
    shell_mock.assert_called_once_with(['python', 'ssd.py', 'E', '0', '5'], text=True)
    file_mock.assert_any_call('ssd_output.txt', 'r')
    assert ret == "[Erase] Done"


def test_erase_range_mock(file_mock, shell_mock):
    ret = Shell.execute_command(cmd=ShellCommandEnum.ERASE_RANGE, args=[10, 30])
    assert shell_mock.call_count == 3
    shell_mock.assert_called_with(['python', 'ssd.py', 'E', '30', '1'], text=True)
    file_mock.assert_any_call('ssd_output.txt', 'r')
    assert ret == "[Erase Range] Done"


def test_flush_mock(file_mock, shell_mock):
    ret = Shell.execute_command(cmd=ShellCommandEnum.FLUSH, args=[])
    shell_mock.assert_called_once_with(['python', 'ssd.py', 'F'], text=True)
    file_mock.assert_any_call('ssd_output.txt', 'r')
    assert ret == '[Flush] Done'


def test_script_1_mock(file_mock, shell_mock):
    Shell.execute_command(cmd=ShellCommandEnum.SCRIPT_1, args=[])
    shell_mock.assert_called_with(['python', 'ssd.py', 'R', '0'], text=True)
    file_mock.assert_any_call('ssd_output.txt', 'r')


def test_script_2_mock(file_mock, shell_mock):
    Shell.execute_command(cmd=ShellCommandEnum.SCRIPT_2, args=[])
    shell_mock.assert_called_with(['python', 'ssd.py', 'R', '4'], text=True)
    file_mock.assert_any_call('ssd_output.txt', 'r')


def test_script_3_mock(file_mock, shell_mock):
    Shell.execute_command(cmd=ShellCommandEnum.SCRIPT_3, args=[])
    assert shell_mock.call_count == 200 * 4
    shell_mock.assert_called_with(['python', 'ssd.py', 'R', '99'], text=True)
    file_mock.assert_any_call('ssd_output.txt', 'r')


def test_script_4_mock(file_mock, shell_mock):
    num_iter_test = 5
    ret = Shell.execute_command(cmd=ShellCommandEnum.SCRIPT_4, args=[num_iter_test])
    assert shell_mock.call_count == 1 + num_iter_test * 49 * 3
    shell_mock.assert_called_with(['python', 'ssd.py', 'E', '98', "2"], text=True)
    file_mock.assert_any_call('ssd_output.txt', 'r')
    assert ret == MESSAGE_PASS


def test_write_and_read(ssd_py_path):
    lba = 3
    val = "0x30003000"
    ret = Shell.execute_command(cmd=ShellCommandEnum.WRITE, args=[lba, val])
    assert ret == "[Write] Done"

    ret = Shell.execute_command(cmd=ShellCommandEnum.READ, args=[lba])
    assert ret == f"[Read] LBA {lba:02d} : {val}"


def test_write(ssd_py_path):
    ret = Shell.execute_command(cmd=ShellCommandEnum.WRITE, args=[3, "0x00000003"])
    assert ret == "[Write] Done"


def test_full_write_and_read(ssd_py_path):
    val = "0x40004000"
    ret = Shell.execute_command(cmd=ShellCommandEnum.FULLWRITE, args=[val])
    assert ret == "[Full Write] Done"

    expected = "[Full Read]"
    for lba in range(SIZE_LBA):
        expected += f"\nLBA {lba:0>2} : {val}"
    ret = Shell.execute_command(cmd=ShellCommandEnum.FULLREAD, args=[])
    assert ret == expected


def test_full_write(ssd_py_path):
    ret = Shell.execute_command(cmd=ShellCommandEnum.FULLWRITE, args=["0x00000000"])
    assert ret == "[Full Write] Done"


def test_exit(ssd_py_path):
    pass


def test_help():
    ret = Shell.execute_command(cmd=ShellCommandEnum.HELP, args=[])
    assert ret == MESSAGE_HELP


def test_find_invalid_command(ssd_py_path):
    ret = Shell.shell_parser.find_command(command_str="wow")
    assert ret == ShellCommandEnum.INVALID


def test_erase(ssd_py_path):
    ret = Shell.execute_command(cmd=ShellCommandEnum.ERASE, args=[0, 5])
    assert ret == "[Erase] Done"


def test_erase_range(ssd_py_path):
    ret = Shell.execute_command(cmd=ShellCommandEnum.ERASE_RANGE, args=[10, 30])
    assert ret == "[Erase Range] Done"


def test_flush(ssd_py_path):
    ret = Shell.execute_command(cmd=ShellCommandEnum.FLUSH, args=[])
    assert ret == "[Flush] Done"


def test_script_1(ssd_py_path):
    ret = Shell.execute_command(cmd=ShellCommandEnum.SCRIPT_1, args=[])
    assert ret == MESSAGE_PASS


def test_script_2(ssd_py_path):
    ret = Shell.execute_command(cmd=ShellCommandEnum.SCRIPT_2, args=[])
    assert ret == MESSAGE_PASS


def test_script_3(ssd_py_path):
    ret = Shell.execute_command(cmd=ShellCommandEnum.SCRIPT_3, args=[])
    assert ret == MESSAGE_PASS


def test_script_4(ssd_py_path):
    num_iter_test = 3
    ret = Shell.execute_command(cmd=ShellCommandEnum.SCRIPT_4, args=[num_iter_test])
    assert ret == MESSAGE_PASS


def test_run_function(monkeypatch, capsys):
    inputs = iter(["read 100", "", "exit"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    ret = Shell.run()
    captured = capsys.readouterr()
    assert captured.out == "[Read] ERROR\n"
    
    
def test_run_script(ssd_py_path, capsys):
    test_script = "test_shell_script.txt"
    expected = ('1_FullWriteAndReadCompare   ___   Run...Pass\n'
                '2_PartialLBAWrite           ___   Run...Pass\n')
    with open(test_script, "w") as f:
        f.write("1_FullWriteAndReadCompare\n2_PartialLBAWrite")

    Shell.run_script(script=test_script)

    captured = capsys.readouterr()
    assert captured.out == expected
