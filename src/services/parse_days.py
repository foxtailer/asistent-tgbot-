import re
from typing import Tuple


async def parse_days(string: str) -> tuple[str, Tuple[int]]:
    pattern = r"^d?(?:\d+(?:,\d+)*|(?:\d+-\d+))$" 

    async def parse(string):
        if '-' in string:
            days = [int(day) for day in string.split('-')]
            days[-1] += 1  # For range)
            args = tuple(list(range(*days)))
        else:
            args = tuple([int(day) for day in string.split(',')])
        return args

    if re.fullmatch(pattern, string):

        if string[0] == 'd':
            days = ('d', await parse(string[1:]))
        else:
            days = ('', await parse(string))

        return days     
