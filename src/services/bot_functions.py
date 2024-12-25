import random

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.fsm.context import FSMContext

from ..states.user_states import UserState
from . import db_functions


async def play(chat_id: int, user_name: str, state: FSMContext, bot):
    data = await state.get_data()
    data = data['play']  # words:list, args:str, answer:str, right_answers:int size:int, 
    await state.clear()

    # If data send to play first time there no "answer" kay so we set "size" at this moment)
    # "words" are full before first pop
    if not data.get('answer'):
        data['size'] = len(data['words'])
   
    if data['words']:
        word = data['words'].pop()
        
        # Play parametrs 'e', 's', 'n'
        if 'e' in data['args']:
            mod = 2  # eng
        else:
            mod = 1  # rus

        #TODO get rid of keyboard there
        answers = []
        answers.append(word)

        if len(data['words']) >= 3:
            answers += random.sample(data['words'], 3)
        else:
            flag = True
            while flag:
                fake_words = await db_functions.get_word(user_name, 3)
                if word not in fake_words:
                    flag = False
            
            answers += fake_words
        random.shuffle(answers)

        for_kb = []
        
        for answer in answers:
            btn_data = answer[mod].capitalize(), 'True' if answer[mod]==word[mod] else 'False'
            for_kb.append(btn_data)

        ibtn1 = InlineKeyboardButton(text=f"{for_kb[0][0]}",callback_data=f"{for_kb[0][1]}")
        ibtn2 = InlineKeyboardButton(text=f"{for_kb[1][0]}", callback_data=f"{for_kb[1][1]}")
        ibtn3 = InlineKeyboardButton(text=f"{for_kb[2][0]}",callback_data=f"{for_kb[2][1]}")
        ibtn4 = InlineKeyboardButton(text=f"{for_kb[3][0]}", callback_data=f"{for_kb[3][1]}")
        ikb = InlineKeyboardMarkup(inline_keyboard=[[ibtn1,ibtn2],[ibtn3,ibtn4]])
        kb = ikb if 'n' not in data['args'] else None

        if 's' in data['args']:

            text = word[3].lower().replace(word[1], '****').capitalize()
            test_msg = await bot.send_message(chat_id, text, reply_markup=kb)   
        else:

            text = f'{word[2 if mod == 1 else 1].capitalize()}:'
            test_msg = await bot.send_message(chat_id, text, reply_markup=kb)

        if data.get('test_msg'):
            await bot.delete_message(chat_id=chat_id, message_id=data['test_msg'])

        data.update({'answer': word[mod]})
        data.update({'test_msg': test_msg.message_id})
        await state.set_state(UserState.play)
        await state.update_data(play=data)

    else:
        await state.clear()
        await bot.delete_message(chat_id=chat_id, 
                                 message_id=data['test_msg'])
        await bot.send_message(chat_id, 
                               text=f"Test is over!\nNice job!\n{data['right_answers']}/{data['size']}")
