import re
import pytest
from pytest_mock import MockerFixture
from ssd import SSD, FileManager


def test_write_and_read(mocker: MockerFixture):
    mock_file_manager = mocker.Mock()
    ssd = SSD(mock_file_manager)

    lba = 0
    expected = "0x12345678"
    ssd.write(lba, expected)
    ssd.read(lba)

    mock_file_manager.read_nand_txt.assert_called_once()
    mock_file_manager.write_nand_txt.assert_called_once()
    mock_file_manager.write_output_txt.assert_called()

def test_read_ssd_nand_txt_file_called_by_read(mocker: MockerFixture):
    mock_file_manager = mocker.Mock()
    ssd = SSD(mock_file_manager)

    lba = 0
    ssd.read(lba)

    mock_file_manager.read_nand_txt.assert_called_once()
    mock_file_manager.write_output_txt.assert_called_once()


def test_read_ssd_nand_txt_file_called_by_write(mocker: MockerFixture):
    mock_file_manager = mocker.Mock(spec=FileManager)
    ssd = SSD(mock_file_manager)

    lba = 0
    write_contents = "0x00001111"
    ssd.write(lba, write_contents)

    mock_file_manager.write_nand_txt.assert_called()


def test_read_method_record_ssd_output_txt(mocker: MockerFixture):
    mock_file_manager = mocker.Mock(spec=FileManager)
    ssd = SSD(mock_file_manager)

    lba = 0
    ssd.read(lba)

    mock_file_manager.read_nand_txt.assert_called()
    mock_file_manager.write_output_txt.assert_called()


def test_write_ssd(mocker: MockerFixture):
    mock_file_manager = mocker.Mock(spec=FileManager)
    ssd = SSD(mock_file_manager)
    lba = 3
    ssd.write(lba, "0xFFFFFFFF")

    mock_file_manager.write_nand_txt.assert_called()


def test_write_check_file(mocker: MockerFixture):
    mock_file_manager = mocker.Mock(spec=FileManager)
    ssd = SSD(mock_file_manager)
    lba = 11
    ssd.write(lba, "0x1298CDEF")

    mock_file_manager.write_nand_txt.assert_called()


def test_out_of_index_error(mocker: MockerFixture):
    mock_file_manager = mocker.Mock(spec=FileManager)
    ssd = SSD(mock_file_manager)
    lba = 120
    ssd.write(lba, "0x1298CDEF")

    mock_file_manager.write_nand_txt.assert_not_called()
    
