from aiogram import Router, types
from aiogram.filters import Command

from src.services import db_functions
from src.services.parse_days import parse_days
from src.config import DB_PATH


del_router = Router()


@del_router.message(Command("del"))
async def del_commmand(msg: types.Message, command):
    """"
    To delete words or whole day from dictionary you can use:
    <code>/del [day]|[word]</code>
    day and word can be sequence:
    <code>/del 2,5</code>
    or range:
    <code>/del 3-15</code>
    If you want deleate day, use 'd' before numbers:
    <code>/del d 3,6</code>
    """

    error_msg = "Need number argument! Like this:\n/del 5\nor\n/del 5,7,12\n"\
                "To deleate sequense of words use:\n/del 5-12"\
                "To deleate whole day type 'd' before command arguments, like:\n/del d 3" 

    if command.args:

        args = command.args.replace(' ', '').strip()

        if (days := await parse_days(args)):

            if await db_functions.del_from_db(msg.from_user.first_name, days, db_path=DB_PATH):
                await msg.answer("Sucsess.")
            else:
                await msg.answer("Failure.")
        else:
            await msg.answer(error_msg)

    await msg.delete()
