from enum import Enum

class CFGNodeTypes(Enum):
    COMMON = 1
    IF = 2
    ELSE = 3
    ELSE_IF = 4
    FOR = 5
    WHILE = 6
    DO_WHILE = 7
    PSEUDO = 8
