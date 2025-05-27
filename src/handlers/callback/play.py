from aiogram import types, Router
from aiogram.fsm.context import FSMContext

from src.states.user_states import UserState
from src.services import  bot_functions


play_call_router = Router()


@play_call_router.callback_query(UserState.play)
async def choice_callback(callback: types.CallbackQuery, state: FSMContext, bot):
    data = await state.get_data()
    #await state.clear()
    data = data['play']
    user_id = callback.from_user.id
    amount = data['size']

    if data.get('right_answers') == None:
        data['right_answers'] = 0

    if data.get('score_msg'):
        await bot.delete_message(callback.message.chat.id, message_id=data['score_msg'])

    if callback.data == "True":
        data['right_answers'] += 1

        msg = await callback.message.answer(text=f"✅ {data['right_answers']}/{amount} [{data['answer']}]")

    elif callback.data == "False": 
        msg = await callback.message.answer(text=f"❌ {data['right_answers']}/{amount} [{data['answer']}]")
        
    data['score_msg'] = msg.message_id
    #await state.set_state(UserState.play)    
    await state.update_data(play=data)
    await bot_functions.play(user_id, callback.from_user.first_name, state, bot=bot)
