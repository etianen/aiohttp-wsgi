def force_str(value):
    return str(value, "latin1") if isinstance(value, (bytes, bytearray, memoryview)) else str(value)


def parse_sockname(sockname):
    if isinstance(sockname, tuple):
        return force_str(sockname[0]), force_str(sockname[1])
    return "unix", force_str(sockname)


def get_kwdefaults(fn):  # pragma: no cover
    # HACK: This is really weird. In some Python runtimes, you can access __kwdefaults__ directly.
    # In other Python runtimes, you have to use __wrapped__. This keeps everyone happy.
    try:
        return fn.__kwdefaults__.copy()
    except AttributeError:
        return get_kwdefaults(fn.__wrapped__)
