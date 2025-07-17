from enum import Enum


class ShellCommandEnum(Enum):
    WRITE = "write"
    READ = "read"
    FULLWRITE = "fullwrite"
    FULLREAD = "fullread"
    ERASE = "erase"
    ERASE_RANGE = "erase_range"
    FLUSH = "flush"
    HELP = "help"
    EXIT = "exit"
    SCRIPT_1 = "1_FullWriteAndReadCompare"
    SCRIPT_2 = "2_PartialLBAWrite"
    SCRIPT_3 = "3_WriteReadAging"
    SCRIPT_4 = "4_EraseAndWriteAging"
    INVALID = "invalid"


SIZE_LBA = 100

FILENAME = "ssd_nand.txt"
FILENAME_OUT = "ssd_output.txt"
FILENAME_MAIN_SSD = "ssd.py"
FILENAME_SCRIPT_DEFAULT = "shell_script.txt"

LOG_FILE_MAX_SIZE = 10 * 1024
LOG_FILE_NAME = "latest.log"
LOG_METHOD_NAME_WIDTH = 30
PAST_LOG_FILE_FORMAT = "until_%y%m%d_%Hh_%Mm_%Ss.log"

MESSAGE_DONE = "DONE"
MESSAGE_ERROR = "ERROR"
MESSAGE_FAIL = "FAIL"
MESSAGE_PASS = "PASS"
MESSAGE_INVALID_SHELL_CMD = "Invalid shall command."
MESSAGE_HELP = """
         ／＞　 フ
        | 　_　_| 
       ／` ミ＿xノ 
      /　　　　 |
     /　 ヽ　　 ﾉ
    │　　|　|　|
／￣|　　 |　|　|
(￣ヽ＿_ヽ_)__)
＼二) ... Dooly Let`s go !!!

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
