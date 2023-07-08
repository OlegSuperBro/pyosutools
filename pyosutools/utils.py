import struct
import datetime


# PART OF CODE COPIED FROM https://github.com/jaasonw/osu-db-tools
def read_bool(buffer) -> bool:
    return struct.unpack("<?", buffer.read(1))[0]


def read_ubyte(buffer) -> int:
    return struct.unpack("<B", buffer.read(1))[0]


def read_ushort(buffer) -> int:
    return struct.unpack("<H", buffer.read(2))[0]


def read_uint(buffer) -> int:
    return struct.unpack("<I", buffer.read(4))[0]


def read_float(buffer) -> float:
    return struct.unpack("<f", buffer.read(4))[0]


def read_double(buffer) -> float:
    return struct.unpack("<d", buffer.read(8))[0]


def read_ulong(buffer) -> int:
    return struct.unpack("<Q", buffer.read(8))[0]


# osu specific
def read_int_double(buffer):
    read_ubyte(buffer)
    integer = read_uint(buffer)
    read_ubyte(buffer)
    double = read_double(buffer)
    return (integer, double)


def read_timing_point(buffer):
    bpm = read_double(buffer)
    offset = read_double(buffer)
    inherited = read_bool(buffer)
    return (bpm, offset, inherited)


def read_string(buffer, encoding: str = "utf-8") -> str:
    strlen = 0
    strflag = read_ubyte(buffer)
    if (strflag == 0x0b):
        strlen = 0
        shift = 0
        # uleb128
        # https://en.wikipedia.org/wiki/LEB128
        while True:
            byte = read_ubyte(buffer)
            strlen |= ((byte & 0x7F) << shift)
            if (byte & (1 << 7)) == 0:
                break
            shift += 7
    return (struct.unpack("<" + str(strlen) + "s", buffer.read(strlen))[0]).decode(encoding)
# PART OF CODE COPIED FROM https://github.com/jaasonw/osu-db-tools


def read_datetime(buffer) -> datetime.datetime:
    ticks = read_ulong(buffer)
    if ticks >= 621355968000000000:
        return datetime.datetime.fromtimestamp((ticks-621355968000000000)/10_000_000, tz=datetime.timezone.utc)
    else:
        return datetime.datetime.min
