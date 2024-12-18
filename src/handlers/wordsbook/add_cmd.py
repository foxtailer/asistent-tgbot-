from aiogram import Router, types
from aiogram.filters import Command

from services import db_functions


add_router = Router()
script_dir = db_functions.find_path()


@add_router.message(Command("add"))
async def add_commmand(msg: types.Message, command):
    if command.args:
        if await db_functions.add_to_db(msg.from_user.first_name, command.args.strip(),
                                        script_dir):
            await msg.answer(msg.chat.id, f"Sucsess!",)
        else:
            await msg.answer(msg.chat.id, f"Wrong sintax!",)
    else:
        await msg.answer(msg.chat.id, 
                            f"Pls tipe words you want to add after <b>/add</b> command.\n\n"
                            "<code>/add eng,rus,exsample</code>\n\n"
                            "Example can be empty but ',' stil nesesary. To add multiple sets of words, just conect them by coma."
                            "Inside example simbol '<b>,</b>' is forbiden!")