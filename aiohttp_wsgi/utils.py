from __future__ import annotations
from typing import Tuple


def parse_sockname(sockname: Tuple | str) -> Tuple[str, str]:
    if isinstance(sockname, tuple):
        return sockname[0], str(sockname[1])
    return "unix", sockname
