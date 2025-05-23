import re
from typing import Tuple


async def parse_days(string: str) -> tuple[str, Tuple[int]]:
    '''
    Parse days/words range from comands args.
    'd' - default flag for 'days'.
    [w]{[\d,\d...]|[\d-\d]|[\d]}  else => None
    
    >>> import asyncio
    >>> asyncio.run(parse_days('v10-12'))  # onlly 'w' allower as first letter flag
    None
    >>> asyncio.run(parse_days('10-12'))
    ('d', (10, 11, 12))
    >>> asyncio.run(parse_days('w10-12'))
    ('w', (10, 11, 12))
    >>> asyncio.run(parse_days('10'))
    ('d', (10,))
    >>> asyncio.run(parse_days('w10'))
    ('w', (10,))
    >>> asyncio.run(parse_days('10,15,2'))
    ('d', (10, 15, 2))
    >>> asyncio.run(parse_days('10-15,2'))
    ('d', (10, 11, 12, 13, 14, 15, 2))
    >>> asyncio.run(parse_days('2,4-6'))
    ('d', (2, 4, 5, 6))
    '''

    flag = 'd'

    if string.startswith('w'):
        flag = 'w'
        string = string[1:]
    elif string[0].isalpha():
        return None

    # Validate format: digits only, optionally separated by , or -
    if not re.fullmatch(r"\d+([,-]\d+)*", string):
        return None

    parts = string.split(',')
    result = []

    try:
        for part in parts:
            if '-' in part:
                start, end = map(int, part.split('-'))
                if start > end:
                    return None
                result.extend(range(start, end + 1))
            else:
                result.append(int(part))
        return (flag, tuple(result))
    except Exception:
        return None


async def parse_test_args(arg_str):
    '''
    Extract arguments for /test command.
    Current args: {s|e}[n]{[r[\d]|[w][<days_range>]} else => None
    
    >>> import asyncio
    >>> asyncio.run(parse_test_args('se10'))
    None
    >>> asyncio.run(parse_test_args('r10,12'))  # random mode acept only one value(emount of words)
    None
    >>> asyncio.run(parse_test_args('sn10'))
    {'flags': 'ns', 'rand_n': 0, 'days': ('d', (10,))}
    >>> asyncio.run(parse_test_args('10,8'))
    {'flags': '', 'rand_n': 0, 'days': ('d', (10, 8))}
    >>> asyncio.run(parse_test_args('10-13'))
    {'flags': '', 'rand_n': 0, 'days': ('d', (10, 11, 12, 13))}
    >>> asyncio.run(parse_test_args('w10-13'))
    {'flags': '', 'rand_n': 0, 'days': ('w', (10, 11, 12, 13))}
    >>> asyncio.run(parse_test_args('r10'))
    {'flags': '', 'rand_n': 10, 'days': ()}
    >>> asyncio.run(parse_test_args('enr10'))
    {'flags': 'en', 'rand_n': 10, 'days': ()}
    '''

    # Extract 'r' mode
    r_match = re.search(r'r(\d+)', arg_str)
    rand_n = int(r_match.group(1)) if r_match else 0

    # Remove r group and extract flags
    arg_wo_r = re.sub(r'r\d+', '', arg_str)
    flags_found = re.findall(r'[sen]', arg_wo_r)
    flags = ''.join(sorted(set(flags_found)))

    # s and e must not appear together
    if 's' in flags_found and 'e' in flags_found:
        return None

    # Remove flags to isolate day range
    remainder = re.sub(r'[sen]', '', arg_wo_r).strip()

    # If in random mode, reject any day range
    if rand_n:
        if remainder:
            return None
        return {'flags': flags, 'rand_n': rand_n, 'days': ()}

    # Parse day range
    days = await parse_days(remainder if remainder else '')
    if days is None:
        return None

    return {'flags': flags, 'rand_n': 0, 'days': days}


if __name__ == '__main__':
    import doctest
    doctest.testmod()
