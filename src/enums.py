from enum import Enum


class ActionQueuePickle(Enum):
    ADD = 1,
    REMOVE = 2


class InitType(Enum):
    LIST = 1,
    SET = 2,
    DICT = 3


class FileType(Enum):
    JSON = 1,
    PICKLE = 2