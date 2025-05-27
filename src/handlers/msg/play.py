from aiogram import types, Router
from aiogram.fsm.context import FSMContext

from src.states.user_states import UserState
from src.services import bot_functions


play_msg_router = Router()


@play_msg_router.message(UserState.play)
async def play_msg(msg: types.Message, state: FSMContext, bot):
    data = await state.get_data()
    data = data['play']
    user_id = msg.from_user.id
    amount = data['size']

    if data.get('right_answers') == None:
        data['right_answers'] = 0

    if data.get('score_msg'):
        await bot.delete_message(msg.chat.id, message_id=data['score_msg'])

    if msg.text.lower() == data['answer']:
        data['right_answers'] += 1

        answer = await msg.answer(text=f"✅ {data['right_answers']}/{amount} [{data['answer']}]")

    else: 
        answer = await msg.answer(text=f"❌ {data['right_answers']}/{amount} [{data['answer']}]")

    data['score_msg'] = answer.message_id   
    await state.update_data(play=data)
    await bot_functions.play(user_id, msg.from_user.first_name, state, bot=bot)
    await msg.delete()
