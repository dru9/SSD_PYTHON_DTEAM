import random
from typing import Union

from constant import SIZE_LBA


def safe_int(value: str | int):
    try:
        return int(value)
    except ValueError:
        return value


def get_random_value(num_digit: int = 8, format_hexadecimal: bool = True) -> str:
    value: int = random.randint(0, int("9" * num_digit))
    value: str = str(value).zfill(num_digit)
    if format_hexadecimal:
        return f"0x{value}"
    return value


def get_two_diff_random_value(num_digit: int = 8, format_hexadecimal: bool = True) -> tuple:
    value1 = get_random_value(num_digit, format_hexadecimal)
    value2 = get_random_value(num_digit, format_hexadecimal)
    while value2 == value1:
        value2 = get_random_value()

    return value1, value2


def validate_erase_args(lba: int, size: int) -> bool:
    if not isinstance(lba, int):
        return False
    if not isinstance(size, int):
        return False

    start, end = (lba, lba + size)
    if start < 0:
        return False
    if end > SIZE_LBA:
        return False
    if size < 1 or size > SIZE_LBA:
        return False
    return True


def validate_erase_range_args(start_lba: int, end_lba: int) -> bool:
    if not isinstance(start_lba, int):
        return False
    if not isinstance(end_lba, int):
        return False

    if start_lba < 0 or start_lba > SIZE_LBA - 1:
        return False

    if end_lba < 0 or end_lba > SIZE_LBA - 1:
        return False

    if start_lba > end_lba:
        return False

    return True


def validate_hexadecimal(data: str) -> bool:
    num_hex = 16
    num_digit = 8
    header = "0x"

    if not data[:2] == header:
        return False

    if len(data) != len(header) + num_digit:
        return False

    try:
        int(data[len(header):], num_hex)
        return True

    except ValueError:
        return False


def validate_index(num: str, valid_size: int) -> bool:
    return num.isdigit() and 0 <= int(num) <= valid_size - 1


def parse_integer(num: str) -> Union[int, str]:
    try:
        return int(num)
    except ValueError:
        return ""
