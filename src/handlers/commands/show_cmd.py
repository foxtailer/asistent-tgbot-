import re

from aiogram import Router, types, Bot
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove

from ...states.user_states import UserState
from ...services import db_functions
from ...services.parse_days import parse_days

# TODO print errors iw user ask for day that dont exist.

show_router = Router()


@show_router.message(Command("show"))
async def show_commmand(msg: types.Message, state:FSMContext, command, sort="Time"):

    error_msg = "Need number argument! Like this:\n/show 5\nor\n/show 5,7,12\n"\
                "To show sequense of deys use:\n/show 5-12"
    
    pattern = r"^(\d+(,\d+)*|\d+-\d+)$"

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
        args = command.args.replace(' ', '').strip()

        if re.fullmatch(pattern, args):
            args = await parse_days(args)
            current_dict = await db_functions.get_day(msg.from_user.first_name, args[1])
        else:
            await msg.answer(error_msg)
    else:
        current_dict = await db_functions.get_all(msg.chat.first_name)

    # current_dict
    # {1: [WordRow(id=28, eng='vargant', rus='бродяга', example='and vargant ronin Jin', day='2024-08-13', lvl=0),],
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


@show_router.callback_query(UserState.show)
async def callback_show(callback: types.CallbackQuery, state: FSMContext, bot):
    data = await state.get_data()  # {'show': {1: [10749,], msg:...}}
    data = data['show']
    args = callback.data.split('_')

    class FakeComand():
        ...
    fake_comand=FakeComand()
    fake_comand.args = args[1]
    
    if args[0] == "Alphabet":
        for msg_id in data[int(args[1])]:
            await bot.delete_message(chat_id=callback.message.chat.id, message_id=msg_id)

        await show_commmand(data['msg'], state, fake_comand, sort="Alphabet")
    elif args[0] == "Examples":
        for msg_id in data[int(args[1])]:
            await bot.delete_message(chat_id=callback.message.chat.id, message_id=msg_id)

        await show_commmand(data['msg'], state, fake_comand, sort="Examples")
    elif args[0] == "Time":
        for msg_id in data[int(args[1])]:
            await bot.delete_message(chat_id=callback.message.chat.id, message_id=msg_id)

        await show_commmand(data['msg'], state, fake_comand)
    elif args[0] == "Close":
        for msg_id in data[int(args[1])]:
            await bot.delete_message(chat_id=callback.message.chat.id, message_id=msg_id)


@show_router.message(Command("clear"), UserState.show)
async def slear_show(msg, state: FSMContext, bot: Bot):
    data = await state.get_data()  # {'show': {1: [10749,], msg:...}}
    data = data['show']
    #await bot.edit_message_reply_markup(chat_id=msg.chat.id, message_id=data['msg'].message_id, reply_markup=None)
    await bot.deleate_message(chat_id=msg.chat.id, message_id=data['msg'].message_id)
