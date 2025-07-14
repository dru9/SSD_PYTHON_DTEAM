from enum import Enum


class CommandEnum(Enum):
    WRITE = "write"
    READ = "read"
    FULLWRITE = "fullwrite"
    FULLREAD = "fullread"
    HELP = "help"
    EXIT = "exit"
    SCRIPT_1 = "1_"
    SCRIPT_2 = "2_"
    SCRIPT_3 = "3_"
    INVALID = "invalid"


VALUE_REQUIRE_COMMANDS = [CommandEnum.WRITE, CommandEnum.FULLWRITE]
