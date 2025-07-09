import re
from datetime import datetime

from src.services.types_ import Word, WordRow


async def args_day_word_validate(args_: str) -> dict | None:
    """
    >>> import asyncio
    >>> asyncio.run(args_day_word_validate('10-12'))
    {'flags': ('w',), 'range': (10, 11, 12)}
    >>> asyncio.run(args_day_word_validate('w10-13'))
    {'flags': ('w',), 'range': (10, 11, 12, 13)}
    >>> asyncio.run(args_day_word_validate('10'))
    {'flags': ('w',), 'range': (10,)}
    >>> asyncio.run(args_day_word_validate('w10'))
    {'flags': ('w',), 'range': (10,)}
    >>> asyncio.run(args_day_word_validate('d10,15,2'))
    {'flags': ('d',), 'range': (10, 15, 2)}
    >>> asyncio.run(args_day_word_validate('d10-15,2'))
    {'flags': ('d',), 'range': (10, 11, 12, 13, 14, 15, 2)}
    >>> asyncio.run(args_day_word_validate('d2,4-6'))
    {'flags': ('d',), 'range': (2, 4, 5, 6)}
    >>> asyncio.run(args_day_word_validate('hello'))
    {'flags': ('s',), 'words': ('hello',)}
    >>> asyncio.run(args_day_word_validate('foo,bar,baz'))
    {'flags': ('s',), 'words': ('foo', 'bar', 'baz')}
    """

    # New: check if args_ is sequence of words without digits and without d/w flag
    if re.fullmatch(r'[a-zA-Z]+(,[a-zA-Z]+)*', args_):
        words = tuple(args_.split(','))
        return {"flags": ('s',), "words": words}

    # Regex: optional flag (letters up to 5) + digits/ranges part
    m = re.fullmatch(r'([a-zA-Z]{1,5})?(\d+([,-]\d+)*)', args_)
    if not m:
        return None

    flag_part = m.group(1)
    numbers_part = m.group(2)

    flag = flag_part if flag_part else 'w'

    result = []

    for part in numbers_part.split(','):
        if '-' in part:
            start_str, end_str = part.split('-', 1)
            start, end = int(start_str), int(end_str)
            if start > end:
                return None
            result.extend(range(start, end+1))
        else:
            result.append(int(part))

    return {"flags": (flag,), "range": tuple(result)}


async def args_add_validate(args_, user_id):
    result = [element.lower().strip() for element in args_.split(',')]

    if (len(result) % 3) != 0:
        return False
    
    # Made list of tuples[(word, translation, example),...]
    result = [tuple(result[i:i + 3]) for i in range(0, len(result), 3)]

    result = [
        {
            'language': ('EN', 'RU'),
            'word': Word(word=w, tg_id=user_id),
            'trans': (Word(word=t, tg_id=user_id),),
            'date': datetime.now().strftime('%Y-%m-%d'),
            'example': ((ex,),)
        }
        for w, t, ex in result
    ]

    result = [WordRow(**w) for w in result]

    return result


# async def parse_test_args(args_):
#     '''
#     Extract arguments for /test command.
#     Current args: {s|e} [n] {[r\d | [w|d][<days_range>]} else => None
    
#     >>> import asyncio
#     >>> asyncio.run(parse_test_args('se10'))
#     None
#     >>> asyncio.run(parse_test_args('r10,12'))  # random mode acept only one value(emount of words)
#     None
#     >>> asyncio.run(parse_test_args('sn10'))
#     {'flags': 'ns', 'rand_n': 0, 'days': ('d', (10,))}
#     >>> asyncio.run(parse_test_args('10,8'))
#     {'flags': '', 'rand_n': 0, 'days': ('d', (10, 8))}
#     >>> asyncio.run(parse_test_args('10-13'))
#     {'flags': '', 'rand_n': 0, 'days': ('d', (10, 11, 12, 13))}
#     >>> asyncio.run(parse_test_args('w10-13'))
#     {'flags': '', 'rand_n': 0, 'days': ('w', (10, 11, 12, 13))}
#     >>> asyncio.run(parse_test_args('r10'))
#     {'flags': '', 'rand_n': 10, 'days': ()}
#     >>> asyncio.run(parse_test_args('enr10'))
#     {'flags': 'en', 'rand_n': 10, 'days': ()}
#     '''

#     # Extract 'r' mode
#     r_match = re.search(r'r(\d+)', args_)
#     rand_n = int(r_match.group(1)) if r_match else 0

#     # Remove r group and extract flags
#     arg_wo_r = re.sub(r'r\d+', '', args_)
#     flags_found = re.findall(r'[sen]', arg_wo_r)
#     flags = ''.join(sorted(set(flags_found)))

#     # s and e must not appear together
#     if 's' in flags_found and 'e' in flags_found:
#         return None

#     # Remove flags to isolate day range
#     remainder = re.sub(r'[sen]', '', arg_wo_r).strip()

#     # If in random mode, reject any day range
#     if rand_n:
#         if remainder:
#             return None
#         return {'flags': flags, 'rand_n': rand_n, 'days': ()}

#     # Parse day range
#     days = await args_day_word_validate(remainder if remainder else '')
#     if days is None:
#         return None

#     return {'flags': flags, 'rand_n': 0, 'days': days}


if __name__ == '__main__':
    import doctest
    doctest.testmod()
