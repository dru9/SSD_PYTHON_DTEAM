import pytest

from constant import MESSAGE_HELP, MESSAGE_PASS, ShellCommandEnum
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
    Shell.execute_command(ShellCommandEnum.READ, [0])
    shell_mock.assert_called_once_with(['python', 'ssd.py', 'R', '0'], text=True)
    file_mock.assert_called_once_with('ssd_output.txt', 'r')


def test_write_mock(file_mock, shell_mock):
    Shell.execute_command(ShellCommandEnum.WRITE, [3, 0x00000000])
    shell_mock.assert_called_once_with(['python', 'ssd.py', 'W', '3', 0], text=True)
    file_mock.assert_called_once_with('ssd_output.txt', 'r')


def test_full_read_mock(file_mock, shell_mock):
    Shell.full_read()
    shell_mock.assert_called_with(['python', 'ssd.py', 'R', '99'], text=True)
    file_mock.assert_called_with('ssd_output.txt', 'r')


def test_full_write_mock(file_mock, shell_mock):
    Shell.full_write(3)
    shell_mock.assert_called_with(['python', 'ssd.py', 'W', '99', 3], text=True)
    file_mock.assert_called_with('ssd_output.txt', 'r')


def test_read(ssd_py_path):
    res = Shell.read(lba=0)
    assert res == "[Read] LBA 00 : 0x00000000"


def test_write(ssd_py_path):
    res = Shell.write(
        lba=3,
        value="0x00000000"
    )
    assert res == "[Write] Done"


def test_full_read(ssd_py_path):
    ret = "[Full Read]"
    for i in range(100):
        ret += f"\nLBA {i:0>2} : 0x00000000"
    res = Shell.full_read()
    assert res == ret


def test_full_write(ssd_py_path):
    res = Shell.full_write(value="0x00000000")
    assert res == "[Full Write] Done"


def test_exit(ssd_py_path):
    pass


def test_help(capsys):
    Shell.execute_command(cmd=ShellCommandEnum.HELP, args=[])
    captured = capsys.readouterr()
    assert MESSAGE_HELP in captured.out


def test_find_invalid_command(ssd_py_path):
    res = Shell.shell_parser.find_command(command_str="wow")
    assert res == ShellCommandEnum.INVALID


def test_script_1(ssd_py_path):
    res = Shell.script_1()
    assert res == MESSAGE_PASS


def test_script_2(ssd_py_path):
    res = Shell.script_2()
    assert res == MESSAGE_PASS


def test_script_3(ssd_py_path):
    res = Shell.script_3()
    assert res == MESSAGE_PASS
