from datetime import datetime

from aiogram import Router, types
from aiogram.filters import Command

from src.services import db_functions
from src.services.types_ import WordRow, Word


add_router = Router()


@add_router.message(Command("add"))
async def add_commmand(msg: types.Message, command, conn):

    error_msg = \
                "Pls tipe words you want to add after <b>/add</b> command.\n\n"\
                "<code>/add word,translation,exsample</code>\n\n"\
                "Example can be empty but ',' stil nesesary.\n\n"\
                "<code>/add word,translation,,word,translation,example</code>\n\n"\
                "To add multiple sets of words, just conect them by coma." \
                "Inside example, simbol '<b>,</b>' is forbiden!"\
                "Coma after last set lead to error."
    
    if (args := command.args):
        words = await args_str_validate(args, msg.from_user.id)

        if not words:
            await msg.answer(error_msg)
            return

        if await db_functions.add_to_db(msg.from_user.id, words, conn):
            await msg.answer("Sucsess!")
        else:
            await msg.answer("Error!")
    else:
        await msg.answer(error_msg)


async def args_str_validate(args_, user_id):
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