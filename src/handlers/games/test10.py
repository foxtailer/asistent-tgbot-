from aiogram import  types, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from ...states.user_states import UserState
from ...services import db_functions, bot_functions


test10_router = Router()


@test10_router.message(Command("test10"))
async def test10(msg: types.Message, command, state:FSMContext, bot):
    await state.set_state(UserState.play)

    if not (command.args and (args := command.args.strip().replace(' ', '')) 
            in ('e', 's', 'n', 'en', 'sn')):
        args = ''

    user_name = msg.from_user.first_name
    words = await db_functions.get_word(user_name, 10)
    
    new_data = {}
    new_data['words'] = words  # list[WordRow,]
    new_data['args'] = args

    await state.update_data(play=new_data)
    await bot_functions.play(msg.chat.id, user_name, state, bot=bot)
    await msg.delete()
