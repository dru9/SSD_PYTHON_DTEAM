import re
import pytest
from pytest_mock import MockerFixture
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

