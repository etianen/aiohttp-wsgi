def parse_sockname(sockname):
    if isinstance(sockname, tuple):
        return sockname[0], str(sockname[1])
    return "unix", sockname
