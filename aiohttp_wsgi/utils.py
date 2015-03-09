def parse_sockname(sockname):
    if isinstance(sockname, tuple):
        return str(sockname[0]), str(sockname[1])
    return "unix", str(sockname)
