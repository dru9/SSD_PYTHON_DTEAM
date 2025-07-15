import random


def get_random_value(num_digit: int = 8, format_hexadecimal: bool = True) -> str:
    value: int = random.randint(0, int("9" * num_digit))
    value: str = str(value).zfill(num_digit)
    if format_hexadecimal:
        return f"0x{value}"
    return value
