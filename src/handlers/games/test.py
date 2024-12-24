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

    if not (command.args and (args := command.args.strip().replace(' ', '')) in ('e', 'w', 'sw', 'ws', 's')):
        args = ()

    if current_state == UserState.day:
        data = await state.get_data()
        data = data['day']
        # {'days': {
        #     1: [WordRow(),...],
        #     ....
        #   },
        # 'day_size': 1,
        # 'day_answers': 0,
        # 'args': ()}
        words = [word for day in data['days'].values() for word in day]
        data['words'] = words
        data.update({'day_size': len(words)})
        data.update({'day_answers': 0})
        data.update({'args': args})

        await state.update_data(test=data)
        await bot_functions.play(msg.chat.id, user_name, state, bot=bot)
    else:
        await bot.send_message(msg.chat.id, 'Pls select day.')

    await msg.delete()
