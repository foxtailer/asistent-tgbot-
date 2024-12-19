import re
from typing import Tuple

from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from ...states.user_states import UserState
from ...services import db_functions


show_router = Router()


@show_router.message(Command("show"))
async def show_commmand(msg: types.Message, state:FSMContext, command, sort="Time"):

    error_msg = "Need number argument! Like this:\n/show 5\nor\n/show 5,7,12\n"\
                "To show sequense of deys use:\n/show 5-12"
    
    pattern = r"^(\d+(,\d+)*|\d+-\d+)$"

    
    async def parse_days(string: str) -> Tuple[int]:
        if '-' in string:
            args = tuple(list(range([int(day) for day in string.split('-')])))
        else:
            args = tuple([int(day) for day in string.split(',')])
        return args
    
    await state.set_state(UserState.show)

    list_of_chunks = []
    msg_chunk = ""
    data = {}

    if command.args:
        args = command.args.replace(' ', '').strip()

        if re.fullmatch(pattern, args):
            args = parse_days(args)
            curent_dict = await db_functions.get_day(msg.from_user.first_name, 
                                                        args)
        else:
            await msg.answer(msg.chat.id, error_msg)
    else:
        curent_dict = await db_functions.get_all(msg.chat.first_name)
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

        show_msg = await msg.answer(list_of_chunks[i], reply_markup=ikb)
        
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