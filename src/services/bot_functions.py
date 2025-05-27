import random

from aiogram.fsm.context import FSMContext

from src.services import db_functions
from src.keyboards import play_ikb
from src.config import DB_PATH


async def play(chat_id: int, user_name: str, state: FSMContext, bot):
    data = await state.get_data()
    data = data['play']  # words:list, args:str, answer:str, right_answers:int size:int, 
    await state.set_data({})

    # If data send to play first time there no "answer" kay so we set "size" at this moment)
    # "words" are full before first pop
    if not data.get('answer'):
        data['size'] = len(data['words'])
        random.shuffle(data['words'])  # for diferent order, each time we play same day
   
    if data['words']:
        word = data['words'].pop()
        
        # type of clue in answer
        if 'e' in data['args']:
            mod = 2  # eng  (need swap answers language)
        else:
            mod = 1  # rus

        answers = []
        answers.append(word)

        # 'n' - mode without answers
        if 'n' not in data['args']:
            # add 3 fake answers to list --------------
            if len(data['words']) >= 3:
                answers += random.sample(data['words'], 3)
            else:
                flag = True
                while flag:  # Maby better save some reserver words in state instead of buther db
                    fake_words = await db_functions.get_word(user_name, 3, db_path=DB_PATH)
                    if word not in fake_words:
                        flag = False
                answers += fake_words
            random.shuffle(answers)
            # -----------------------------------------

            # prepare and create keyboard -------------
            for_kb = []
            for answer in answers:
                btn_data = answer[mod].capitalize(), 'True' if answer[mod]==word[mod] else 'False'
                for_kb.append(btn_data)
            kb = await play_ikb(for_kb)
            #------------------------------------------
        else:
            kb = None

        if 's' in data['args']:
            question_text = word[3].lower().replace(word[1], '****').capitalize()
            test_msg = await bot.send_message(chat_id, question_text, reply_markup=kb)   
        else:
            question_text = f'{word[2 if mod == 1 else 1].capitalize()}:'
            test_msg = await bot.send_message(chat_id, question_text, reply_markup=kb)

        # deleate previous question
        if data.get('test_msg'):
            await bot.delete_message(chat_id=chat_id, message_id=data['test_msg'])

        data['answer'] = word[mod]
        data['test_msg'] = test_msg.message_id
        await state.update_data(play=data)

    else:
        await state.clear()
        await bot.delete_message(chat_id=chat_id,  message_id=data['test_msg'])
        await bot.send_message(chat_id, 
                               text=f"Test is over!\nNice job!\n{data['right_answers']}/{data['size']}")
