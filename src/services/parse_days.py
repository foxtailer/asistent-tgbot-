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


async def parse_test_args(arg_str):
    # Extract flags (s, e, n) — make sure no duplicates
    flags = ''.join(sorted(set(re.findall(r'[sen]', arg_str))))

    # Extract r\d+
    r_match = re.search(r'r\d+', arg_str)
    r_value = r_match.group(0) if r_match else ''

    # Remove flags and r-group from input
    cleaned = re.sub(r'[sen]', '', arg_str)
    cleaned = re.sub(r'r\d+', '', cleaned)

    # The remaining part is the digit group, if any
    digit_group = cleaned if cleaned else ''

    return {
        'flags': flags or '',
        'r': r_value,
        'days': digit_group
    }
