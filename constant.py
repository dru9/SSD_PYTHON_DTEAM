from enum import Enum


class ShellCommandEnum(Enum):
    WRITE = "write"
    READ = "read"
    FULLWRITE = "fullwrite"
    FULLREAD = "fullread"
    HELP = "help"
    EXIT = "exit"
    SCRIPT_1 = "1_FullWriteAndReadCompare"
    SCRIPT_2 = "2_PartialLBAWrite"
    SCRIPT_3 = "3_WriteReadAging"
    INVALID = "invalid"


FILENAME = "ssd_nand.txt"
FILENAME_OUT = "ssd_output.txt"
FILENAME_MAIN_SSD = "ssd.py"

MESSAGE_DONE = "DONE"
MESSAGE_ERROR = "ERROR"
MESSAGE_FAIL = "FAIL"
MESSAGE_PASS = "PASS"
MESSAGE_HELP = """
usage: <command> [<args>]

read: read a value from the given LBA
write: write a given value to the given LBA
exit: terminate the program
help: lists available subcommands
fullwrite: write to all of the LBAs
fullread: read all of the LBAs
test scripts:
    1_FULLWriteAndReadCompare: write random values to the LBAs
    2_PartialLBAWrite: write random values partially and validate all the values are same
    3_WriteReadAging: write random value to LBAs repeatedly and validate the values are same all the time

Team Leader: 송주환
Team Members: 김희준, 박혜녹, 윤다영, 정동혁, 한누리, 오지은
"""

MESSAGE_INVALID_SHELL_CMD = "Invalid shall command."
