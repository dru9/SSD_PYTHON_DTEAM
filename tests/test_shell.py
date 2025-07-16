import pytest

from constant import MESSAGE_HELP, MESSAGE_PASS, ShellCommandEnum
from shell import Shell


@pytest.fixture
def ssd_py_path(mocker):
    return mocker.patch("shell.FILENAME_MAIN_SSD", new="../ssd.py")


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
