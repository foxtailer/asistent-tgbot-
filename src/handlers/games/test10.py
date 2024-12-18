from aiogram import  types, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from src.states.states import UserState

from services import db_functions, bot_functions


test10_router = Router()
script_dir = db_functions.find_path()


@test10_router.message(Command("start"))
async def test10(msg: types.Message, command, state:FSMContext, bot):
    await state.set_state(UserState.test)

    if command.args and command.args.strip() in ('e', 'w', 's w', 'w s', 's'):
        args = command.args.strip().split()
    else:
        args = ()

    user_name = msg.from_user.first_name
    day = await db_functions.get_word(script_dir, user_name, 10)
    tmp = {'day': day, 'day_size': 10, 'day_answers': 0, 'args': args}

    await state.update_data(test=tmp)
    await bot_functions.play(msg.chat.id, user_name, state, bot=bot)

    await msg.delete()