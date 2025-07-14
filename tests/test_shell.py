import pytest
from pytest_mock import MockerFixture


def test_shell_read(mocker: MockerFixture):
    shell = mocker.Mock()
    shell.read.return_value = "[Read] LBA 00 : 0x00000000"
    res = shell.read(lba=0)
    assert res == "[Read] LBA 00 : 0x00000000"
    shell.read.assert_called()


def test_shell_write(mocker: MockerFixture):
    shell = mocker.Mock()
    shell.write.return_value = "[Write] Done"
    res = shell.write(
        lba=3,
        value="0x00000000"
    )
    assert res == "[Write] Done"
    shell.write.assert_called()
