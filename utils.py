import random


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
