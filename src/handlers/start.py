from aiogram import  types, Router
from aiogram.filters import CommandStart

import db_functions
from main import bot


user_private_router = Router()
script_dir = db_functions.find_path()


@user_private_router.message(CommandStart())
async def start_commmand(msg: types.Message):
    
    text = "We hope our bot can help you learn any language :)"
    if await db_functions.check_user(msg.from_user.first_name, script_dir):
        await bot.send_message(msg.chat.id, 
                               f"""Hello {msg.from_user.first_name}! 👋\n{text}\n
You can select bot language.
(Выберите язык ботаю)\n
<code>/help</code> for more details.""", 
                               parse_mode="HTML")
    else:
        await bot.send_message(msg.chat.id, 
                               f"""Welcome {msg.from_user.first_name}! 👋\n{text}\n
You can select bot language.
(Выберите язык ботаю)\n
<code>/help</code> for more details.""", 
                               parse_mode="HTML")
    await msg.delete()