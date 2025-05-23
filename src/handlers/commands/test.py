import re

from aiogram import  types, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from ...states.user_states import UserState
from ...services import bot_functions, db_functions
from ...services.parse_days import parse_test_args


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
    
    # pattern = re.compile(r'^([sen]*)(r\d+)?(\d+(?:,\d+)*|\d+-\d+|\d+)?$')

    # # 1 are 'default day' TODO store it in cash. it should be last day we use for test
    # args = '1' if command.args is None else command.args.strip().replace(' ', '')
    # match = pattern.fullmatch(args)

    # if match:
    #     play_args, rand_flag, days = match.group(1), match.group(2), match.group(3)
    # else:
    #     play_args = ''

    # # args = await parse_test_args(args)
    # # play_args, rand_flag, days = args['flags'], args['r'], args['days']

    if command.args:
        args = await parse_test_args(command.args.replace(' ', '').strip())

        if args:
            play_args, rand_flag, days = args['flags'], args['rand_n'], args['days']
            user_name = msg.from_user.first_name
            new_data = {}
            new_data['args'] = play_args

            if rand_flag:
                new_data['words'] = await db_functions.get_word(user_name, rand_flag)  # list[WordRow,]
                await state.update_data(play=new_data)
                await bot_functions.play(msg.chat.id, user_name, state, bot=bot)
            else:
                days = await db_functions.get_day(msg.from_user.first_name,  days[1])  # dict{int:list[WordRow,]}
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
