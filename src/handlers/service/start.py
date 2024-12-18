from aiogram import  types, Router
from aiogram.filters import Command

from services import db_functions, variables


start_router = Router()
script_dir = db_functions.find_path()


@start_router.message(Command("start"))
async def start_commmand(msg: types.Message):
    
    text = "We hope our bot can help you learn any language :)"

    if await db_functions.check_user(msg.from_user.first_name, script_dir):
        await msg.answer(msg.chat.id, 
                            f'Hello {msg.from_user.first_name}! 👋\n{text}\n'
                                'You can select bot language.'
                                '(Выберите язык ботаю)\n'
                                '<code>/help</code> for more details')
    else:
        await msg.answer(msg.chat.id, 
                            f'Welcome {msg.from_user.first_name}! 👋\n{text}\n'
                                'You can select bot language.'
                                '(Выберите язык ботаю)\n'
                                '<code>/help</code> for more details.')
    await msg.delete()


@start_router.message(Command("help"))
async def help_commmand(msg: types.Message):
    message = variables.HELP_MESSAGE_ENG
    await msg.answer(msg.chat.id, message)
    await msg.delete()