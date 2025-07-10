from aiogram import Router, types
from aiogram.filters import Command

from src.services.db_functions import del_from_db, get_info
from src.services.parse_args import args_day_word_validate


del_router = Router()


@del_router.message(Command("del"))
async def del_commmand(msg: types.Message, command, conn):
    
    error_msg = \
                "To delete words or whole day from dictionary you can use:\n\n"\
                "<code>/del [d|w] 1 | 1,3,4 | 2-5</code>\n\n"\
                "w - default flag so /del ... is the same as /del w ...\n"\
                "1 - mean exect day or word id\n"\
                "1,3,4 - mean sequense of exect days or word ids\n"\
                "2-5 - mean range of day/words from 2 to 5(2,3,4,5)"
    
    if (args := command.args):
        args = await args_day_word_validate(args.replace(' ', '').strip())

        if args:
            if await del_from_db(msg.from_user.id, args, conn):
                await msg.answer("Sucsess.")
            else:
                await msg.answer("Failure.")
        else:
            await msg.answer(error_msg)

    else:
        words, days = (tmp := await get_info(msg.from_user.id, conn))[0]
        await msg.answer(f'You have words:{words}, days:{days}\n\n' + error_msg)

    await msg.delete()
