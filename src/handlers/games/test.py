from aiogram import  types, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from ...states.user_states import UserState
from ...services import bot_functions


test_router = Router()


@test_router.message(Command("test"))
async def test(msg: types.Message, command, state:FSMContext, bot):
    current_state = await state.get_state()
    user_name = msg.from_user.first_name

    await state.set_state(UserState.test)

    if command.args and command.args.strip() in ('e', 'w', 's w', 'w s', 's'):
        args = command.args.strip().split()
    else:
        args = ()

    if current_state is None:
        await bot.send_message(msg.chat.id, 'Pls select day.')
    elif current_state == UserState.test:
        data = await state.get_data()
        data = data['test']
        data.update({'args': args})
        
        await state.update_data(test=data)
        await bot_functions.play(msg.chat.id, user_name, state, bot=bot)

    await msg.delete()