from datetime import datetime

from aiogram import Router, types
from aiogram.filters import Command

from src.services import db_functions
from src.services.types_ import WordRow, Word
from src.services.parse_args import args_add_validate


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
        words = await args_add_validate(args, msg.from_user.id)

        if not words:
            await msg.answer(error_msg)
            return

        if await db_functions.add_to_db(msg.from_user.id, words, conn):
            await msg.answer("Sucsess!")
        else:
            await msg.answer("Error!")
    else:
        await msg.answer(error_msg)
