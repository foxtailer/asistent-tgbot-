from aiogram import types, Router
from aiogram.fsm.context import FSMContext

from ..states.user_states import UserState
from ..services import db_functions, bot_functions


hz_router = Router()
script_dir = db_functions.find_path()


@hz_router.message(UserState.write)
async def write(msg: types.Message, state: FSMContext, bot):
    data = await state.get_data()
    data = data['test']
    right_answer = data['write_answer']

    if data.get('score') and data['flag']:
        await bot.delete_message(msg.chat.id, message_id=data['score'])

    if right_answer.lower().strip() == msg.text.lower().strip():
        if data['flag']:
            data['day_answers'] += 1
            score = await msg.answer(text=f"✅ {data['day_answers']}/{data['day_size']}")
            data['score'] = score.message_id

        await state.set_state(UserState.test)
        await state.update_data(data)
        await bot_functions.play(msg.from_user.id, msg.from_user.first_name, state, bot=bot)
    else:
        await msg.deleate()
        if data['flag']:
            score = await bot.send_message(msg.chat.id, 
                                            f"❌ {data['day_answers']}/{data['day_size']}", 
                                            parse_mode="HTML")
            data['score'] = score.message_id
            data['flag'] = False
            await state.update_data(data)
        await bot.send_message(msg.chat.id, f"{right_answer}", parse_mode="HTML")


@hz_router.callback_query(UserState.test)
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