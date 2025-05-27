import random

from aiogram import types, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from src.states.user_states import UserState
from src.services import db_functions
from src.config import DB_PATH


shuffle_router = Router()


@shuffle_router.message(Command("shuffle"))
async def shuffle_play(msg: types.Message, state: FSMContext):
    user_name = msg.from_user.first_name

    await state.set_state(UserState.shuffle)

    word = await db_functions.get_word(user_name, db_path=DB_PATH)
    shuffled_word = list(word[0][1])
    random.shuffle(shuffled_word)

    data = {'shuffle_clue': 0, 
                'shuffle_word': word[0][1],
                'shuffle_rus': word[0][2],
                'shuffle_ex': word[0][3],
                'shuffled_word':shuffled_word}
    
    text = '_'.join(shuffled_word)
    
    ibtn1 = InlineKeyboardButton(text="Help", callback_data="shuffle_help")
    ikb = InlineKeyboardMarkup(inline_keyboard=[[ibtn1]])

    #await bot.send_message(msg.chat.id, DiceEmoji.SLOT_MACHINE, reply_markup=None)
    shuffle_msg = await msg.answer(text, reply_markup=ikb)

    data['shuffle_msg'] = shuffle_msg.message_id
    await state.update_data(shuffle=data)

    await msg.delete()
