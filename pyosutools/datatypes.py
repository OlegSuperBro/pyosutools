from aenum import Enum, IntFlag


class GameMode(Enum):
    """
    osu! gamemodes
    """
    STD = 0
    TAIKO = 1
    CTB = 2
    MANIA = 3


class Mod(IntFlag):
    """
    osu! mods or their combination
    """
    NM = 0
    NF = 1 << 0
    EZ = 1 << 1
    TD = 1 << 2
    HD = 1 << 3
    HR = 1 << 4
    SD = 1 << 5
    DT = 1 << 6
    RX = 1 << 7
    HT = 1 << 8
    NC = 1 << 9
    FL = 1 << 10
    AT = 1 << 11
    SO = 1 << 12
    AP = 1 << 13
    PF = 1 << 14
    K4 = 1 << 15
    K5 = 1 << 16
    K6 = 1 << 17
    K7 = 1 << 18
    K8 = 1 << 19
    FD = 1 << 20
    RD = 1 << 21
    CN = 1 << 22
    TP = 1 << 23
    K9 = 1 << 24
    CO = 1 << 25
    K1 = 1 << 26
    K3 = 1 << 27
    K2 = 1 << 28
    V2 = 1 << 29
    MR = 1 << 30