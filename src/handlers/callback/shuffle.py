from aiogram import types, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from src.states.user_states import UserState


shuffle_call_router = Router()


@shuffle_call_router.callback_query(UserState.shuffle)
async def callback_shuffle(callback: types.CallbackQuery, state: FSMContext, bot):
    if callback.data == "shuffle_help":
        data = await state.get_data()
        data = data['shuffle']
    
        data['shuffle_clue'] += 1
        clue = data['shuffle_clue']
        word = list(data['shuffle_word'])
        shuffled_word = data['shuffled_word'].copy()

        if clue < len(word):
            clue_letters = word[0:clue]
            
            for letter in clue_letters:
                shuffled_word.remove(letter)

            text = '_'.join([letter.upper() for letter in clue_letters] + shuffled_word)

            ibtn1 = InlineKeyboardButton(text="Help", callback_data="shuffle_help")
            ikb = InlineKeyboardMarkup(inline_keyboard=[[ibtn1]])

            await bot.edit_message_text(
                        chat_id=callback.message.chat.id,
                        message_id=data['shuffle_msg'],
                        text=text,
                        reply_markup=ikb)
            
            await state.update_data(shuffle=data)

        elif clue == len(word):
            clue_letters = word[0:clue]

            for letter in clue_letters:
                shuffled_word.remove(letter)

            text = '_'.join([letter.upper() for letter in clue_letters] + shuffled_word)

            await bot.edit_message_text(
                        chat_id=callback.message.chat.id,
                        message_id=data['shuffle_msg'],
                        text=text)
            
            await state.update_data(shuffle=data)