from aiogram import types, Router
from aiogram.fsm.context import FSMContext

from ..states.user_states import UserState
from ..services import db_functions, bot_functions


hz_router = Router()


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
