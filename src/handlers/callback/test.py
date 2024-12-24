from aiogram import types, Router
from aiogram.fsm.context import FSMContext

from ...states.user_states import UserState
from ...services import  bot_functions


test_call_router = Router()


@test_call_router.callback_query(UserState.test)
async def choice_callback(callback: types.CallbackQuery, state: FSMContext, bot):
    data = await state.get_data()
    data = data['test']
    user_id = callback.from_user.id
    amount = data['day_size']
    right_answer = data['day_answers']
    
    if callback.data == "True":
        data['day_answers'] += 1

        if data.get('score'):
            await bot.delete_message(callback.message.chat.id, message_id=data['score'])

        msg = await callback.message.answer(text=f"✅ {right_answer}/{amount}")
        data['score'] = msg.message_id
        await state.update_data(test=data)

        await bot_functions.play(user_id, callback.from_user.first_name, state, bot=bot)

    elif callback.data == "False": 

        if data.get('score'):
            await bot.delete_message(callback.message.chat.id, message_id=data['score'])

        msg = await callback.message.answer(text=f"❌ {right_answer}/{amount}")
        data['score'] = msg.message_id
        await state.update_data(test=data)

        await bot_functions.play(user_id, callback.from_user.first_name, state, bot=bot)