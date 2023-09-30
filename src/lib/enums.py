from enum import Enum


class Protocol(Enum):
    STOP_AND_WAIT = "STOP_AND_WAIT"
    SELECTIVE_REPEAT = "SELECTIVE_REPEAT"


class Action(Enum):
    UPLOAD = "UPLOAD"
    DOWNLOAD = "DOWNLOAD"
