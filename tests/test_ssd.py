import pytest
from pytest_mock import MockerFixture

from ssd import SSD, FileManager
import re


def test_write_and_read(mocker: MockerFixture):
    mock_file_manager = mocker.Mock()
    ssd = SSD(mock_file_manager)

    lba = 0
    expected = "0x12345678"
    ssd.write(lba, expected)
    ssd.read(lba)

    mock_file_manager._read_nand_txt.assert_called()
    mock_file_manager.read_nand.assert_called_once()
    mock_file_manager.write_nand.assert_called_once()
    mock_file_manager.write_output.assert_called_once()


def test_read_ssd_nand_txt_file_called_by_read(mocker: MockerFixture):
    mock_file_manager = mocker.Mock()
    ssd = SSD(mock_file_manager)

    read_idx = 0
    ssd.read(read_idx)

    mock_file_manager._read_nand_txt.assert_called()
    mock_file_manager.read_nand.assert_called_once()
    mock_file_manager.write_output.assert_called_once()


def test_read_ssd_nand_txt_file_called_by_write(mock: MockerFixture):
    mock_file_manager = mock.Mock(spec=FileManager)
    ssd = SSD(mock_file_manager)

    write_idx = 0
    write_contents = "0x00001111"
    ssd.write(write_idx, write_contents)

    mock_file_manager._read_whole_contents_nand_txt.assert_called()
    mock_file_manager.write_nand_txt.assert_called()


def test_read_method_record_ssd_output_txt(mock: MockerFixture):
    mock_file_manager = mock.Mock(spec=FileManager)
    ssd = SSD(mock_file_manager)

    read_idx = 0
    ssd.read(read_idx)

    mock_file_manager.read_nand_txt.assert_called()
    mock_file_manager.write_output_txt.assert_called()


def test_write_ssd(mock: MockerFixture):
    mock_file_manager = mock.Mock(spec=FileManager)
    ssd = SSD(mock_file_manager)
    loc = 3
    ssd.write(loc, "0xFFFFFFFF")

    mock_file_manager.write_nand_txt.assert_called()


def test_write_check_file():
    ssd = SSD()
    loc = 11
    ssd.write(loc, "0x1298CDEF")

    with open("ssd_output.txt", "r") as f:
        content = f.read()
    assert content == ""


def test_out_of_index_error():
    ssd = SSD()
    loc = 120
    ssd.write(loc, "0x1298CDEF")

    with open("ssd_output.txt", "r") as f:
        content = f.read()
    assert content == "ERROR"
