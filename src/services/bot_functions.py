import random
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from states import UserState

import db_functions

script_dir = db_functions.find_path()

async def play(chat_id, user_name, state, bot):
    data = await state.get_data()
    data = data['test']

    words = data['day']
    args = data['args']
   
    if words:
        word = words.pop()
        
        if 'e' in args:
            mod = 2

        if 'w' not in args:
            answers = []
            answers.append(word)

            if len(words) >= 3:
                answers += random.sample(words, 3)
            else:
                flag = True
                while flag:
                    fake_words = await db_functions.get_word(script_dir, user_name, 3)
                    if word not in fake_words:
                        flag = False
                
                answers += fake_words
            random.shuffle(answers)

            for_kb = []
            mod = 1
            
            for answer in answers:
                btn_data = answer[mod].capitalize(), 'True' if answer[mod]==word[mod] else 'False'
                for_kb.append(btn_data)

            ibtn1 = InlineKeyboardButton(text=f"{for_kb[0][0]}",callback_data=f"{for_kb[0][1]}")
            ibtn2 = InlineKeyboardButton(text=f"{for_kb[1][0]}", callback_data=f"{for_kb[1][1]}")
            ibtn3 = InlineKeyboardButton(text=f"{for_kb[2][0]}",callback_data=f"{for_kb[2][1]}")
            ibtn4 = InlineKeyboardButton(text=f"{for_kb[3][0]}", callback_data=f"{for_kb[3][1]}")
            ikb = InlineKeyboardMarkup(inline_keyboard=[[ibtn1,ibtn2],[ibtn3,ibtn4]])

            if 's' in args:
                text = word[3].replace(word[1], '****').capitalize()
                test_msg = await bot.send_message(chat_id, text, parse_mode="HTML", reply_markup=ikb)
            else:
                test_msg = await bot.send_message(chat_id, f'{word[2 if mod == 1 else 1].capitalize()}:', parse_mode="HTML", reply_markup=ikb)
        else:
            if len(args) > 1:
                text = word[3].replace(word[1], '****').capitalize()
                test_msg = await bot.send_message(chat_id, text, parse_mode="HTML")
            else:
                test_msg = await bot.send_message(chat_id, word[2], parse_mode="HTML")

            data.update({'write_answer': word[1]})
            await state.set_state(UserState.write)

        if data.get('test_msg'):
            await bot.delete_message(chat_id=chat_id, message_id=data['test_msg'])

        data.update({'test_msg': test_msg.message_id})
        data.update({'flag': True})
        await state.update_data(data)

    else:
        await state.clear()
        await bot.delete_message(chat_id=chat_id, 
                                 message_id=data['test_msg'])
        await bot.send_message(chat_id, 
                               text=f"Test is over!\nNice job!\n{data['day_answers']}/{data['day_size']}")
