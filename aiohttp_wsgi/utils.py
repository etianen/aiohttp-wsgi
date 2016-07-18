def force_str(value):
    return str(value, "latin1") if isinstance(value, (bytes, bytearray, memoryview)) else str(value)


def parse_sockname(sockname):
    if isinstance(sockname, tuple):
        return force_str(sockname[0]), force_str(sockname[1])
    return "unix", force_str(sockname)
