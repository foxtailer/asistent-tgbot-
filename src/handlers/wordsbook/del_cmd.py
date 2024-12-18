from aiogram import Router, types
from aiogram.filters import Command

from services import db_functions


del_router = Router()
script_dir = db_functions.find_path()


@del_router.message(Command("del"))
async def del_commmand(msg: types.Message, command):
    args = command.args.replace(' ', '').strip()

    if args[0] == 'd' and args[1:].replace(',', '').isdigit():
        args = ('d', args[1:]) 
    elif args and args.replace(',', '').isdigit():
        args = ('', args)
    else:
        await msg.answer(msg.chat.id, "Need number argument! Like this:\n/del 5\nor\n/del 5,7,12\n"
                                    "To deleate whole day type 'd' before command, like:\n/del d 3")

    if await db_functions.del_from_db(msg.from_user.first_name, args, script_dir):
        await msg.answer(msg.chat.id, "Sucsess.")
    else:
        await msg.answer(msg.chat.id, "Failure.")

    await msg.delete()