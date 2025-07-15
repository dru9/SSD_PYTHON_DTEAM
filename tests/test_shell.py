from pytest_mock import MockerFixture  # noqa

from consts.commands import CommandEnum
from consts.help_msg import HELP_MSG


def test_read(mocker: MockerFixture):
    shell = mocker.Mock()
    shell.read.return_value = "[Read] LBA 00 : 0x00000000"
    res = shell.read(lba=0)
    assert res == "[Read] LBA 00 : 0x00000000"
    shell.read.assert_called()


def test_write(mocker: MockerFixture):
    shell = mocker.Mock()
    shell.write.return_value = "[Write] Done"
    res = shell.write(
        lba=3,
        value="0x00000000"
    )
    assert res == "[Write] Done"
    shell.write.assert_called()


def test_full_read(mocker: MockerFixture):
    shell = mocker.Mock()
    ret = "[Full Read]"
    for i in range(100):
        ret += f"\nLBA {i:0>2} : 0x00000000"
    shell.full_read.return_value = ret
    res = shell.full_read()
    assert res == ret
    shell.full_read.assert_called()


def test_full_write(mocker: MockerFixture):
    shell = mocker.Mock()
    shell.full_write.return_value = "[Full Write] Done"
    res = shell.full_write(value="0x00000000")
    assert res == "[Full Write] Done"
    shell.full_write.assert_called()


def test_exit(mocker: MockerFixture):
    pass


def test_help(mocker: MockerFixture):
    shell = mocker.Mock()
    shell.execute_command.return_value = HELP_MSG
    res = shell.execute_command(command=CommandEnum.HELP)
    assert res == HELP_MSG


def test_find_invalid_command(mocker: MockerFixture):
    shell = mocker.Mock()
    shell.find_command.return_value = CommandEnum.INVALID
    res = shell.find_command(command_str="wow")
    assert res == CommandEnum.INVALID


def test_script_1(mocker: MockerFixture):
    shell = mocker.Mock()
    shell.script_1.return_value = "PASS"
    res = shell.script_1()
    assert res == "PASS"
    shell.script_1.assert_called()


def test_script_2(mocker: MockerFixture):
    shell = mocker.Mock()
    shell.script_2.return_value = "PASS"
    res = shell.script_2()
    assert res == "PASS"
    shell.script_2.assert_called()


def test_script_3(mocker: MockerFixture):
    shell = mocker.Mock()
    shell.script_3.return_value = "PASS"
    res = shell.script_3()
    assert res == "PASS"
    shell.script_3.assert_called()
