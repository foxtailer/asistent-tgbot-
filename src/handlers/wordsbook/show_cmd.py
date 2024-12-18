import sqlite3

from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from src.states.states import UserState
from services import db_functions


show_router = Router()
script_dir = db_functions.find_path()


@show_router.message(Command("show"))
async def show_commmand(msg: types.Message, state:FSMContext, command, 
                        sort="Time"):
    await state.set_state(UserState.show)

    list_of_chunks = []
    msg_chunk = ""
    data = {}

    if isinstance(command, int):
        if command != 0:
            curent_dict = await db_functions.get_day(script_dir, 
                                                     msg.chat.first_name, 
                                                     command-1)
            args = command
        else:
            connection = sqlite3.connect(f"{script_dir}/{db_functions.DB_NAME}")
            cursor = connection.cursor()
            cursor.execute(f'SELECT * FROM {msg.chat.first_name}')
            # [(371, ' Stain', ' пятно', ' The red wine left a stain on the carpet.', '2024-08-26', 0),]
            curent_dict = cursor.fetchall()  
            connection.close()
            args = 0
    
    else:
        if command.args:
            args = int(command.args.strip())
            curent_dict = await db_functions.get_day(script_dir, msg.from_user.first_name, 
                                                     args-1)
        else:
            connection = sqlite3.connect(f"{script_dir}/{db_functions.DB_NAME}")
            cursor = connection.cursor()
            cursor.execute(f'SELECT * FROM {msg.chat.first_name}')
            # [(371, ' Stain', ' пятно', ' The red wine left a stain on the carpet.', '2024-08-26', 0),]
            curent_dict = cursor.fetchall() 
            connection.close()
            args = 0
    
    longest_word = max(curent_dict, 
                       key=lambda x: len(x[1])
                       )[1]
    len_of_longest_word = len(longest_word)
    
    if sort == "Alphabet":
        curent_dict.sort(key=lambda x: x[1])

        for row in curent_dict:
            if len(msg_chunk) < 2500:
                msg_chunk += f"<code>{row[1].capitalize()}</code>: <pre>{' '*len_of_longest_word + row[2]}</pre>\n"
            else:
                list_of_chunks.append(msg_chunk)
                msg_chunk = ""
                msg_chunk += f"<code>{row[1].capitalize()}</code>: <pre>{' '*len_of_longest_word + row[2]}</pre>\n"

        list_of_chunks.append(msg_chunk)

    elif sort == "Examples":
        for i in curent_dict:
            if len(msg_chunk) < 2500:
                msg_chunk += f"<code>{i[1].capitalize()}</code>: {i[2]} <pre>{i[3].capitalize()}</pre>\n"
            else:
                list_of_chunks.append(msg_chunk)
                msg_chunk = ""
                msg_chunk += f"<code>{i[1].capitalize()}</code>: {i[2]} <pre>{i[3].capitalize()}</pre>\n"

        list_of_chunks.append(msg_chunk)

    else:
        temp_date = ""
        day_count = 1

        for i in curent_dict:
            if i[4] != temp_date:
                msg_chunk += ". "*10 + i[4] + f" ({day_count})" + "\n"
                temp_date = i[4]
                day_count += 1
            if len(msg_chunk) < 2500:
                msg_chunk += f"{i[0]}. <code>{i[1].capitalize()}</code>:  {'  '*(len_of_longest_word-len(i[1]))}{i[2]}\n"
            else:
                list_of_chunks.append(msg_chunk)
                msg_chunk = ""
                msg_chunk += f"{i[0]}. <code>{i[1].capitalize()}</code>:  {'  '*(len_of_longest_word-len(i[1]))}{i[2]}\n"

        list_of_chunks.append(msg_chunk)

    ibtn1 = InlineKeyboardButton(text="Alphabet",callback_data="Alphabet")
    ibtn2 = InlineKeyboardButton(text="Time", callback_data="Time")
    ibtn4 = InlineKeyboardButton(text="Examples", callback_data="Examples")
    
    temp = {}
    for i in range(len(list_of_chunks)):
        ibtn3 = InlineKeyboardButton(text="Close", callback_data=f"Close{i}")
        ikb = InlineKeyboardMarkup(inline_keyboard=[[ibtn1,ibtn2],[ibtn4],[ibtn3]])

        show_msg = await msg.answer(msg.chat.id, 
                                        list_of_chunks[i], 
                                        parse_mode="HTML", 
                                        reply_markup=ikb)
        
        temp[f'Close{i}'] = show_msg.message_id 
    
    data['to_deleate'] = temp
    data['day'] = args
    
    await state.update_data(show=data)

    await msg.delete()


@show_router.callback_query(UserState.show)
async def callback_show(callback: types.CallbackQuery, state: FSMContext, bot):
    data = await state.get_data()
    data = data['show']

    if callback.data in data['to_deleate']:
        await bot.delete_message(chat_id=callback.message.chat.id, message_id=data['to_deleate'][callback.data])

    elif callback.data == "Alphabet":
        await show_commmand(callback.message, state, data['day'], sort="Alphabet")
    elif callback.data == "Examples":
        await show_commmand(callback.message, state, data['day'], sort="Examples")
    elif callback.data == "Time":
        await show_commmand(callback.message, state, data['day'])