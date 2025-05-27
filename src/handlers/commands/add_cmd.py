from aiogram import Router, types
from aiogram.filters import Command

from src.services import db_functions
from src.config import DB_PATH


add_router = Router()


@add_router.message(Command("add"))
async def add_commmand(msg: types.Message, command):

    error_msg = f"Pls tipe words you want to add after <b>/add</b> command.\n\n"\
                "<code>/add eng,rus,exsample</code>\n\n"\
                "Example can be empty but ',' stil nesesary.(rus,eng,,rus,eng,example) To add multiple sets of words, just conect them by coma." \
                "Inside example simbol '<b>,</b>' is forbiden!"
    
    if (data := command.args):
        data = [element.lower().strip() for element in data.split(',')]

        if (len(data) % 3) != 0:
            await msg.answer(error_msg)
            return

        words = [tuple(data[i:i + 3]) for i in range(0, len(data), 3)]

        if await db_functions.add_to_db(msg.from_user.first_name, words, db_path=DB_PATH):
            await msg.answer("Sucsess!")
        else:
            await msg.answer("Error!")
    else:
        await msg.answer(error_msg)
