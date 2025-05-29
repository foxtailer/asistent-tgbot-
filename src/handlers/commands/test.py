import re

from aiogram import  types, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from src.states.user_states import UserState
from src.services import bot_functions, db_functions
from src.services.parse_days import parse_test_args
from src.config import DB_PATH


test_router = Router()


@test_router.message(Command("test"))
async def test(msg: types.Message, command, state:FSMContext, bot):
    """
    Awailable parametrs:
    <code>/test e</code>
    Bot ask word on eng and give variants on rus.
    
    <code>/test s</code>
    Bot ask example sentense with word replased by *s.

    Add 'n' as second parametr if you dont want variants:
    <code>/test e n</code>
    """

    await state.clear()
    await state.set_state(UserState.play)

    if command.args:
        args = await parse_test_args(command.args.replace(' ', '').strip())

        if args:
            play_args, rand_flag, days = args['flags'], args['rand_n'], args['days']
            user_name = msg.from_user.first_name
            new_data = {}
            new_data['args'] = play_args

            if rand_flag:
                new_data['words'] = await db_functions.get_word(user_name, rand_flag, db_path=DB_PATH)  # list[WordRow,]
                await state.update_data(play=new_data)
                await bot_functions.play(msg.chat.id, user_name, state, bot=bot)
            else:
                days = await db_functions.get_day(msg.from_user.first_name,  days[1], db_path=DB_PATH)  # dict{int:list[WordRow,]}
                words = [word for day in days.values() for word in day]
                new_data['words'] = words  # list[WordRow,]

                await state.update_data(play=new_data)
                await bot_functions.play(msg.chat.id, user_name, state, bot=bot)
        else:
            await bot.send_message(msg.chat.id, 'Unsoported arguments combination.')
            await state.clear()
    else:
        #TODO 'default day' store it in cash. it should be last day we use for test
        await bot.send_message(msg.chat.id, 'Require arguments combination.')
        await state.clear()

    await msg.delete()
