import random

from aiogram import types, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from src.states.states import UserState
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup,\
ReplyKeyboardMarkup, KeyboardButton

from services import db_functions


shuffle_router = Router()
script_dir = db_functions.find_path()


@shuffle_router.message(Command("shuffle"))
async def shuffle_play(msg: types.Message, state: FSMContext):
    user_name = msg.from_user.first_name

    await state.set_state(UserState.shuffle)

    word = await db_functions.get_word(script_dir, user_name)
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
    shuffle_msg = await msg.answer(msg.chat.id, text, reply_markup=ikb)

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


@shuffle_router.callback_query(UserState.shuffle)
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