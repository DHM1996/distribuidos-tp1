from enum import Enum


class Protocol(Enum):
    STOP_AND_WAIT = "STOP AND WAIT"


class Action(Enum):
    UPLOAD = "UPLOAD"
    DOWNLOAD = "DOWNLOAD"
