from enum import Enum


class Protocol(Enum):
    STOP_AND_WAIT = "STOP AND WAIT"
    SELECTIVE_REPEAT = "SELECTIVE REPEAT"


class Action(Enum):
    UPLOAD = "UPLOAD"
    DOWNLOAD = "DOWNLOAD"
