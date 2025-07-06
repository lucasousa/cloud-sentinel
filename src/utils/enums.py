from enum import Enum, IntEnum


class UnitType(IntEnum):
    integer = 1
    float = 2
    percentage = 3
    

class Status(IntEnum):
    on = 1
    off = 0


class Action(str, Enum):
    create = "create"
    delete = "delete"
    edit = "edit"
