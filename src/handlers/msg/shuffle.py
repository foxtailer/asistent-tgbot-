from aiogram import types, Router
from aiogram.fsm.context import FSMContext

from src.states.user_states import UserState


shuffle_msg_router = Router()


@shuffle_msg_router.message(UserState.shuffle)
async def shuffle_msg(msg: types.Message, state: FSMContext, bot):
    data = await state.get_data()
    data = data['shuffle']

    if msg.text.lower() == data['shuffle_word']:
        btn = types.KeyboardButton(text="/shuffle")
        rkb = types.ReplyKeyboardMarkup(keyboard=[[btn]], resize_keyboard=True)

        await msg.answer(text=f"✅\n{data['shuffle_word'].capitalize()}: {data['shuffle_rus']}\n"\
                              f"{data['shuffle_ex'].capitalize()}",
                              reply_markup=rkb)
        
        await bot.delete_message(chat_id=msg.chat.id, message_id=data['shuffle_msg'])
        await state.clear()
    else:
        await msg.delete()