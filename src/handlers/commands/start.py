from aiogram import  types, Router
from aiogram.filters import Command

from src.services import db_functions, variables


start_router = Router()


@start_router.message(Command("start"))
async def start_commmand(msg: types.Message):
    await db_functions.init_db()

    text = "We hope our bot can help you learn any language :)"

    if await db_functions.check_user(msg.from_user.first_name):
        await msg.answer(f'Hello {msg.from_user.first_name}! 👋\n{text}\n\n'
                            'You can select bot language.\n'
                            '(Выберите язык бота)\n\n'
                            '<code>/help</code>\nfor more details')
    else:
        await msg.answer(f'Welcome {msg.from_user.first_name}! 👋\n{text}\n\n'
                            'You can select bot language.\n'
                            '(Выберите язык бота)\n\n'
                            '<code>/help</code>\nfor more details.')
    await msg.delete()


@start_router.message(Command("help"))
async def help_commmand(msg: types.Message):
    message = variables.HELP_MESSAGE_ENG
    await msg.answer(message)
    await msg.delete()