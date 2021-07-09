from typing import Tuple, Union


def parse_sockname(sockname: Union[Tuple, str]) -> Tuple[str, str]:
    if isinstance(sockname, tuple):
        return sockname[0], str(sockname[1])
    return "unix", sockname
