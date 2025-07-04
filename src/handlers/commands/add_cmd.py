from datetime import datetime

from aiogram import Router, types
from aiogram.filters import Command

from src.services import db_functions
from src.config import DB_PATH
from src.services.types import Word


async def args_str_validate(args_):
    data = [element.lower().strip() for element in args_.split(',')]

    if (len(data) % 3) != 0:
        return False
 
    words = [tuple(data[i:i + 3]) for i in range(0, len(data), 3)]
    words = [
        {
            'language': ('EN', 'RU'),
            'word': en,
            'trans': ru,
            'date': datetime.now().strftime('%Y-%m-%d'),
            'example': ex
        }
        for en, ru, ex in words
    ]
    words = [Word(**w) for w in words]

    return words


add_router = Router()


@add_router.message(Command("add"))
async def add_commmand(msg: types.Message, command, conn):

    error_msg = f"Pls tipe words you want to add after <b>/add</b> command.\n\n"\
                "<code>/add eng,rus,exsample</code>\n\n"\
                "Example can be empty but ',' stil nesesary.(rus,eng,,rus,eng,example) To add multiple sets of words, just conect them by coma." \
                "Inside example simbol '<b>,</b>' is forbiden!"
    
    if (args := command.args):
        words = await args_str_validate(args)

        if not words:
            await msg.answer(error_msg)
            return

        if await db_functions.add_to_db(msg.from_user.id, words, conn):
            await msg.answer("Sucsess!")
        else:
            await msg.answer("Error!")
    else:
        await msg.answer(error_msg)
