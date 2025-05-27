from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from src.states.user_states import UserState
from src.services import db_functions
from src.services.parse_days import parse_days
from src.config import DB_PATH


# TODO print errors iw user ask for day that dont exist.

show_router = Router()


@show_router.message(Command("show"))
async def show_commmand(msg: types.Message, state:FSMContext, command, sort="Time"):

    error_msg = "Need number argument! Like this:\n/show 5\nor\n/show 5,7,12\n"\
                "To show sequense of deys use:\n/show 5-12"

    if  await state.get_state() != "UserState:show":
        await state.clear()
        await state.set_state(UserState.show)
        data = {}
    else:
        data = await state.get_data()
        data = data['show']

    days_msg = {}
    msg_text = ""

    if command.args:
        args = await parse_days(command.args.replace(' ', '').strip())

        if args:
            if args[0] == 'd':
                current_dict = await db_functions.get_day(msg.from_user.first_name, args[1], db_path=DB_PATH)
            elif args[0] == 'w':
                pass  #TODO show words
        else:
            await msg.answer(error_msg)
    else:
        current_dict = await db_functions.get_all(msg.chat.first_name, db_path=DB_PATH)

    # current_dict
    # {1: [WordRow(id=28, eng='vargant', rus='бродяга', example='and vargant ronin Jin', day='2024-08-13', lvl=0),...],
    #  2: [...],...}

    longest_word = max(list(current_dict.values())[0], key=lambda x: len(x.eng)).eng
    len_of_longest_word = len(longest_word)
    
    if sort == "Alphabet":
        for day in current_dict:
            current_dict[day].sort(key=lambda x: x.eng)

        for day, word_rows in current_dict.items():
            msg_text += ". "*10 + word_rows[0].day + f" ({day})" + "\n\n"
            
            tmp = []

            for word_row in word_rows:
                if len(msg_text) < 2500:
                    msg_text += f"<code>{word_row.eng.capitalize()}</code>: <pre>{' '*len_of_longest_word + word_row.rus}</pre>\n"
                else:
                    tmp.append(msg_text)
                    msg_text = ""
                    msg_text += f"<code>{word_row.eng.capitalize()}</code>: <pre>{' '*len_of_longest_word + word_row.rus}</pre>\n"

            tmp.append(msg_text)
            msg_text = ""
            days_msg[day] = (tuple(tmp))

    elif sort == "Examples":
        for day, word_rows in current_dict.items():
            msg_text += ". "*10 + word_rows[0].day + f" ({day})" + "\n\n"
            
            tmp = []

            for word_row in word_rows:
                if len(msg_text) < 2500:
                    msg_text += f"<code>{word_row.eng.capitalize()}</code>: {word_row.rus} <pre>{word_row.example.capitalize()}</pre>\n"
                else:
                    tmp.append(msg_text)
                    msg_text = ""
                    msg_text += f"<code>{word_row.eng.capitalize()}</code>: {word_row.rus} <pre>{word_row.example.capitalize()}</pre>\n"

            tmp.append(msg_text)
            msg_text = ""
            days_msg[day] = (tuple(tmp))

    else:
        for day, word_rows in current_dict.items():
            msg_text += ". "*10 + word_rows[0].day + f" ({day})" + "\n\n"
            
            tmp = []

            for word_row in word_rows:
                if len(msg_text) < 2500:
                    msg_text += f"{word_row.id}. <code>{word_row.eng.capitalize()}: {' '*(len_of_longest_word - len(word_row.eng))} {word_row.rus}</code>\n"
                else:
                    tmp.append(msg_text)
                    msg_text = ""
                    msg_text += f"{word_row.id}. <code>{word_row.eng.capitalize()}: {' '*(len_of_longest_word - len(word_row.eng))} {word_row.rus}</code>\n"

            tmp.append(msg_text)
            msg_text = ""
            days_msg[day] = (tuple(tmp))
    
    for day, msg_list in days_msg.items():

        if data.get(day):
            data[day].clear()
        else:
            data[day] = []

        ibtn1 = InlineKeyboardButton(text="Alphabet",callback_data=f"Alphabet_{day}")
        ibtn2 = InlineKeyboardButton(text="Time", callback_data=f"Time_{day}")
        ibtn3 = InlineKeyboardButton(text="Examples", callback_data=f"Examples_{day}")
        ibtn4 = InlineKeyboardButton(text="Close", callback_data=f"Close_{day}")

        ikb = InlineKeyboardMarkup(inline_keyboard=[[ibtn1, ibtn2, ibtn3],[ibtn4]])

        for i in range(len(msg_list)):
            if i == len(msg_list) - 1:
                show_msg = await msg.answer(msg_list[i], reply_markup=ikb)
                data[day].append(show_msg.message_id)
            else:
                show_msg = await msg.answer(msg_list[i])
                data[day].append(show_msg.message_id)

    data['msg'] = msg
    await state.update_data(show=data)
    await msg.delete()
