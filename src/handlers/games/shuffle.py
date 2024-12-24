import random

from aiogram import types, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup,\
ReplyKeyboardMarkup, KeyboardButton

from ...states.user_states import UserState
from ...services import db_functions


shuffle_router = Router()


@shuffle_router.message(Command("shuffle"))
async def shuffle_play(msg: types.Message, state: FSMContext):
    user_name = msg.from_user.first_name

    await state.set_state(UserState.shuffle)

    word = await db_functions.get_word(user_name)
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


@shuffle_router.message(UserState.shuffle)
async def listener(msg: types.Message, state: FSMContext, bot):
    data = await state.get_data()
    data = data['shuffle']

    shuffle_word = data['shuffle_word']

    if msg.text.lower() == shuffle_word:
        btn = KeyboardButton(text="/shuffle")
        rkb = ReplyKeyboardMarkup(keyboard=[[btn]], resize_keyboard=True)

        await msg.answer(text=f"✅\n{data['shuffle_word'].capitalize()}: {data['shuffle_rus']}\n\
{data['shuffle_ex'].capitalize()}",
reply_markup=rkb)
        
        await bot.delete_message(chat_id=msg.chat.id, message_id=data['shuffle_msg'])
        await state.clear()
    else:
        await msg.delete()
