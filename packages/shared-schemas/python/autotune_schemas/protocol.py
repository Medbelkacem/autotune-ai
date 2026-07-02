from enum import Enum


class Protocol(str, Enum):
    OBD2 = "OBD2"
    KWP2000 = "KWP2000"
    UDS = "UDS"
    ISO15765 = "ISO15765-4"
    DOIP = "DoIP"
    CAN = "CAN"
    CAN_FD = "CAN_FD"
    J2534 = "J2534"
