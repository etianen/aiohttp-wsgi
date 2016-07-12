from importlib import import_module


def force_str(value):
    return str(value, "latin1") if isinstance(value, (bytes, bytearray, memoryview)) else str(value)


def parse_sockname(sockname):
    if isinstance(sockname, tuple):
        return force_str(sockname[0]), force_str(sockname[1])
    return "unix", force_str(sockname)


def import_func(func):
    if isinstance(func, str):
        assert ":" in func, "{!r} should have format 'module:callable'".format(func)
        module_name, func_name = func.split(":", 1)
        module = import_module(module_name)
        func = getattr(module, func_name)
    assert callable(func), "{!r} is not callable".format(func)
    return func
