from aiogram import  types, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from ...states.user_states import UserState
from ...services import bot_functions, db_functions


test_router = Router()


@test_router.message(Command("test"))
async def test(msg: types.Message, command, state:FSMContext, bot):
    """
    After select day using <code>/select_day</code> command.
    You can start test ower selecting day. You can ask both by
    click on button with answer or by typing answer in chat.

    Awailable parametrs:
    <code>/test e</code>
    Bot ask word on eng and give variants on rus.
    
    <code>/test s</code>
    Bot ask example sentense with word replased by *s.

    Add 'n' as second parametr if you dont want variants:
    <code>/test e n</code>
    """

    current_state = await state.get_state()
    user_name = msg.from_user.first_name

    # if not (command.args and (args := command.args.strip().replace(' ', '')) 
    #         in ('e', 's', 'n', 'en', 'sn')):
    #     args = ''
    args = '' if command.args is None else command.args

    if 'r' in args:
        words = await db_functions.get_word(user_name, 10)
        new_data = {}
        new_data['words'] = words  # list[WordRow,]
        new_data['args'] = args
        await state.update_data(play=new_data)
        await bot_functions.play(msg.chat.id, user_name, state, bot=bot)
    else:
        if current_state == UserState.day:
            data = await state.get_data()
            await state.clear()
            await state.set_state(UserState.play)
            data = data['days'] # dict[int:list[WordRow,],]

            # Preprocess words for play function
            new_data = {}
            words = [word for day in data['days'].values() for word in day]
            new_data['words'] = words  # list[WordRow,]
            new_data['args'] = args

            await state.update_data(play=new_data)
            await bot_functions.play(msg.chat.id, user_name, state, bot=bot)
        else:
            await bot.send_message(msg.chat.id, 'Pls select day.')

    await msg.delete()
