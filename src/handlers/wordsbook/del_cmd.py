from aiogram import Router, types
from aiogram.filters import Command
from typing import Tuple
import re

from ...services import db_functions


del_router = Router()


@del_router.message(Command("del"))
async def del_commmand(msg: types.Message, command):

    error_msg = "Need number argument! Like this:\n/del 5\nor\n/del 5,7,12\n"\
                "To deleate sequense of words use:\n/del 5-12"\
                "To deleate whole day type 'd' before command arguments, like:\n/del d 3"
    
    pattern = r"^d?(?:\d+(?:,\d+)*|(?:\d+-\d+))$"
    
    async def parse_days(string: str) -> Tuple[int]:
        if '-' in string:
            days = [int(day) for day in string.split('-')]
            days[-1] += 1
            args = tuple(list(range(*days)))
        else:
            args = tuple([int(day) for day in string.split(',')])
        return args

    if command.args:
        args = command.args.replace(' ', '').strip()

        if args and re.fullmatch(pattern, args):
            
            if args[0] == 'd':
                args = ('d', await parse_days(args[1:]))
            else:
                args = ('', await parse_days(args))
            
            if await db_functions.del_from_db(msg.from_user.first_name, args):
                await msg.answer("Sucsess.")
            else:
                await msg.answer("Failure.")
        else:
            await msg.answer(error_msg)

    await msg.delete()
