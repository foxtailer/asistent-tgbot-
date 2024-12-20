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
            days = [int(day) for day in string.split('-')]
            days[-1] += 1
            args = tuple(list(range(*days)))
        else:
            args = tuple([int(day) for day in string.split(',')])
        return args
    
    await state.set_state(UserState.show)

    list_of_days = []
    day_msg = ""
    data = {}

    if command.args:
        args = command.args.replace(' ', '').strip()

        if re.fullmatch(pattern, args):
            args = await parse_days(args)
            current_dict = await db_functions.get_day(msg.from_user.first_name, args)
        else:
            await msg.answer(error_msg)
    else:
        current_dict = await db_functions.get_all(msg.chat.first_name)

    # current_dict
    # {1: [WordRow(id=28, eng='vargant', rus='бродяга', example='and vargant ronin Jin', day='2024-08-13', lvl=0),]}

    longest_word = max(list(current_dict.values())[0], key=lambda x: len(x.eng)).eng
    len_of_longest_word = len(longest_word)
    
    if sort == "Alphabet":
        for day in current_dict:
            current_dict[day].sort(key=lambda x: x.eng)

        for day, word_rows in current_dict.items():
            day_msg += ". "*10 + word_rows[0].day + f" ({day})" + "\n\n"
            
            tmp = [day]

            for word_row in word_rows:
                if len(day_msg) < 2500:
                    day_msg += f"<code>{word_row.eng.capitalize()}</code>: <pre>{' '*len_of_longest_word + word_row.rus}</pre>\n"
                else:
                    tmp.append(day_msg)
                    day_msg = ""
                    day_msg += f"<code>{word_row.eng.capitalize()}</code>: <pre>{' '*len_of_longest_word + word_row.rus}</pre>\n"

            tmp.append(day_msg)
            day_msg = ""

            list_of_days.append(tuple(tmp))

    elif sort == "Examples":
        for day, word_rows in current_dict.items():
            day_msg += ". "*10 + word_rows[0].day + f" ({day})" + "\n\n"
            
            tmp = [day]

            for word_row in word_rows:
                if len(day_msg) < 2500:
                    day_msg += f"<code>{word_row.eng.capitalize()}</code>: {word_row.rus} <pre>{word_row.example.capitalize()}</pre>\n"
                else:
                    tmp.append(day_msg)
                    day_msg = ""
                    day_msg += f"<code>{word_row.eng.capitalize()}</code>: {word_row.rus} <pre>{word_row.example.capitalize()}</pre>\n"

            tmp.append(day_msg)
            day_msg = ""

            list_of_days.append(tuple(tmp))

    else:
        for day, word_rows in current_dict.items():
            day_msg += ". "*10 + word_rows[0].day + f" ({day})" + "\n\n"
            
            tmp = [day]

            for word_row in word_rows:
                if len(day_msg) < 2500:
                    day_msg += f"{word_row.id}. <code>{word_row.eng.capitalize()}: {' '*(len_of_longest_word - len(word_row.eng))} {word_row.rus}</code>\n"
                else:
                    tmp.append(day_msg)
                    day_msg = ""
                    day_msg += f"{word_row.id}. <code>{word_row.eng.capitalize()}: {' '*(len_of_longest_word - len(word_row.eng))} {word_row.rus}</code>\n"

            tmp.append(day_msg)
            day_msg = ""

            list_of_days.append(tuple(tmp))
    
    for day in list_of_days:
        day_messages = day[1:]
        day = day[0]
        data[day] = []

        ibtn1 = InlineKeyboardButton(text="Alphabet",callback_data=f"Alphabet_{day}")
        ibtn2 = InlineKeyboardButton(text="Time", callback_data=f"Time_{day}")
        ibtn3 = InlineKeyboardButton(text="Examples", callback_data=f"Examples_{day}")
        ibtn4 = InlineKeyboardButton(text="Close", callback_data=f"Close_{day}")

        ikb = InlineKeyboardMarkup(inline_keyboard=[[ibtn1, ibtn2, ibtn3],[ibtn4]])

        for i in range(len(day_messages)):
            if i == len(day_messages) - 1:
                show_msg = await msg.answer(day_messages[i], reply_markup=ikb)
                data[day].append(show_msg.message_id)
            else:
                show_msg = await msg.answer(day_messages[i])
                data[day].append(show_msg.message_id)
    
    await state.update_data(show=data)

    await msg.delete()


@show_router.callback_query(UserState.show)
async def callback_show(callback: types.CallbackQuery, state: FSMContext, bot):
    data = await state.get_data()  # {'show': {1: [10749]}}
    data = data['show']

    args = callback.data.split('_')

    class Fake():
        ...
    fake=Fake()
    fake.args = args[1]
    
    if args[0] == "Alphabet":
        for msg_id in data[int(args[1])]:
            await bot.delete_message(chat_id=callback.message.chat.id, message_id=msg_id)
        await show_commmand(callback.message, state, fake, sort="Alphabet")
    elif args[0] == "Examples":
        await show_commmand(callback.message, state, fake, sort="Examples")
    elif args[0] == "Time":
        await show_commmand(callback.message, state, fake)
    elif args[0] == "Close":
        ...

