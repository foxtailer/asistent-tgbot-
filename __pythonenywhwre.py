import asyncio
import random
import sqlite3

from aiogram import Bot, types, Dispatcher
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.client.session.aiohttp import AiohttpSession

import db_functions
from bot_cmds_list import private
from bot_functions import play
import variables
from states import UserState

# import sys; sys.path.append('/home/zoy/vscode')
# import deps

session = AiohttpSession(proxy='http://proxy.server:3128')
bot = Bot('1690656566:AAH1aWeuR6AUPs9yjU_UfnstKxr5ALXUcY4', session=session)
dp = Dispatcher()

script_dir = db_functions.find_path()


@dp.message(Command("help"))
async def help_commmand(msg: types.Message):
    message = variables.HELP_MESSAGE
    await bot.send_message(msg.chat.id, message, parse_mode="HTML")
    await msg.delete()


@dp.message(Command("start"))
async def start_commmand(msg: types.Message):

    n = "We hope our bote can help you learn watever you want:)"
    if await db_functions.check_user(msg.from_user.first_name, script_dir):
        await bot.send_message(msg.chat.id,
                               f"Hello {msg.from_user.first_name}!\n{n}\n<code>/help</code> for more details.",
                               parse_mode="HTML")
    else:
        await bot.send_message(msg.chat.id,
                               f"Welcome {msg.from_user.first_name}!\n{n}\n<code>/help</code> for more details.",
                               parse_mode="HTML")
    await msg.delete()


@dp.message(Command("show"))
async def show_commmand(msg: types.Message, state:FSMContext, command, sort="Time"):
    await state.set_state(UserState.show)

    list_of_chunks = []
    msg_chunk = ""
    data = {}

    if isinstance(command, int):
        if command != 0:
            curent_dict = await db_functions.get_day(script_dir, msg.chat.first_name, command-1)
            args = command
        else:
            connection = sqlite3.connect(f"{script_dir}/{db_functions.DB_NAME}")
            cursor = connection.cursor()
            cursor.execute(f'SELECT * FROM {msg.chat.first_name}')
            curent_dict = cursor.fetchall()  # [(371, ' Stain', ' пятно', ' The red wine left a stain on the carpet.', '2024-08-26', 0),]
            connection.close()
            args = 0

    else:
        if command.args:
            args = int(command.args.strip())
            curent_dict = await db_functions.get_day(script_dir, msg.from_user.first_name, args-1)
        else:
            connection = sqlite3.connect(f"{script_dir}/{db_functions.DB_NAME}")
            cursor = connection.cursor()
            cursor.execute(f'SELECT * FROM {msg.chat.first_name}')
            curent_dict = cursor.fetchall()  # [(371, ' Stain', ' пятно', ' The red wine left a stain on the carpet.', '2024-08-26', 0),]
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

        show_msg = await bot.send_message(msg.chat.id,
                                        list_of_chunks[i],
                                        parse_mode="HTML",
                                        reply_markup=ikb)

        temp[f'Close{i}'] = show_msg.message_id

    data['to_deleate'] = temp
    data['day'] = args

    await state.update_data(show=data)

    await msg.delete()


@dp.callback_query(UserState.show)
async def callback_show(callback: types.CallbackQuery, state: FSMContext):
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


@dp.message(Command("add"))
async def add_commmand(msg: types.Message, command):
    if command.args:
        if await db_functions.add_to_db(msg.from_user.first_name, command.args.strip(), script_dir):
            await bot.send_message(msg.chat.id,
                               f"Sucsess!",)
        else:
            await bot.send_message(msg.chat.id,
                               f"Wrong sintax!",)
    else:
        await bot.send_message(msg.chat.id,
                               f"Pls tipe words you want to add after <b>/add</b> command.\n\n \
<code>/add eng,rus,exsample</code>\n\n\
Example can be empty but ',' stil nesesary. To add multiple sets of words, just conect them by coma.\
Inside example simbol '<b>,</b>' is forbiden!",
                               parse_mode="HTML")


@dp.message(Command("del"))
async def del_commmand(msg: types.Message, command):
    args = command.args.replace(' ', '').strip()

    if args[0] == 'd' and args[1:].replace(',', '').isdigit():
        args = ('d', args[1:])
    elif args and args.replace(',', '').isdigit():
        args = ('', args)
    else:
        await bot.send_message(msg.chat.id, "Need number argument! Like this:\n/del 5\nor\n/del 5,7,12\n\
To deleate whole day type 'd' before command, like:\n/del d 3")

    if await db_functions.del_from_db(msg.from_user.first_name, args, script_dir):
        await bot.send_message(msg.chat.id, "Sucsess.")
    else:
        await bot.send_message(msg.chat.id, "Failure.")

    await msg.delete()


@dp.message(Command("select_day"))
async def select_day(msg: types.Message, command, state: FSMContext):
    await state.set_state(UserState.test)

    if command.args and command.args.strip().isdigit():
        day = await db_functions.get_day(script_dir, msg.from_user.first_name,  int(command.args)-1)

        if day:
            tmp = {'day': day, 'day_size': len(day), 'day_answers': 0}

            await state.update_data(test=tmp)
        else:
           await bot.send_message(msg.chat.id,
                                  "Wrong day numder!")
    else:
        await bot.send_message(msg.chat.id,
                               f"Pls tipe number of day you want to select after command.\n\n \
<code>/select_day 3</code>\n\n\
You can finde day number using <code>/show</code> command.",
                               parse_mode="HTML")

    await msg.delete()


@dp.message(Command("test"))
async def test(msg: types.Message, command, state:FSMContext):
    current_state = await state.get_state()
    user_name = msg.from_user.first_name

    await state.set_state(UserState.test)

    if command.args and command.args.strip() in ('e', 'w', 's w', 'w s', 's'):
        args = command.args.strip().split()
    else:
        args = ()

    if current_state is None:
        await bot.send_message(msg.chat.id, 'Pls select day.')
    elif current_state == UserState.test:
        data = await state.get_data()
        data = data['test']
        data.update({'args': args})

        await state.update_data(test=data)
        await play(msg.chat.id, user_name, state, bot=bot)

    await msg.delete()


@dp.message(Command("test10"))
async def test10(msg: types.Message, command, state:FSMContext):
    await state.set_state(UserState.test)

    if command.args and command.args.strip() in ('e', 'w', 's w', 'w s', 's'):
        args = command.args.strip().split()
    else:
        args = ()

    user_name = msg.from_user.first_name
    day = await db_functions.get_word(script_dir, user_name, 10)
    tmp = {'day': day, 'day_size': 10, 'day_answers': 0, 'args': args}

    await state.update_data(test=tmp)
    await play(msg.chat.id, user_name, state, bot=bot)

    await msg.delete()


@dp.message(Command("shuffle"))
async def shuffle_play(msg, state:FSMContext):
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
    shuffle_msg = await bot.send_message(msg.chat.id, text, reply_markup=ikb)

    data['shuffle_msg'] = shuffle_msg.message_id
    await state.update_data(shuffle=data)

    await msg.delete()


@dp.message(UserState.shuffle)
async def listener(msg: types.Message, state: FSMContext):
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


@dp.callback_query(UserState.shuffle)
async def callback_shuffle(callback: types.CallbackQuery, state: FSMContext):
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


@dp.message(UserState.write)
async def write(msg: types.Message, state: FSMContext):
    data = await state.get_data()
    data = data['test']
    right_answer = data['write_answer']

    if data.get('score') and data['flag']:
        await bot.delete_message(msg.chat.id, message_id=data['score'])

    if right_answer.lower().strip() == msg.text.lower().strip():
        if data['flag']:
            data['day_answers'] += 1
            score = await msg.answer(text=f"✅ {data['day_answers']}/{data['day_size']}")
            data['score'] = score.message_id

        await state.set_state(UserState.test)
        await state.update_data(data)
        await play(msg.from_user.id, msg.from_user.first_name, state, bot=bot)
    else:
        if data['flag']:
            score = await bot.send_message(msg.chat.id,
                                            f"❌ {data['day_answers']}/{data['day_size']}",
                                            parse_mode="HTML")
            data['score'] = score.message_id
            data['flag'] = False
            await state.update_data(data)
        await bot.send_message(msg.chat.id, f"{right_answer}", parse_mode="HTML")


@dp.callback_query(UserState.test)
async def choice_callback(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    data = data['test']
    user_id = callback.from_user.id
    amount = data['day_size']
    right_answer = data['day_answers']

    if callback.data == "True":
        data['day_answers'] += 1

        if data.get('score'):
            await bot.delete_message(callback.message.chat.id, message_id=data['score'])

        msg = await callback.message.answer(text=f"✅ {right_answer}/{amount}")
        data['score'] = msg.message_id
        await state.update_data(test=data)

        await play(user_id, callback.from_user.first_name, state, bot=bot)

    elif callback.data == "False":

        if data.get('score'):
            await bot.delete_message(callback.message.chat.id, message_id=data['score'])

        msg = await callback.message.answer(text=f"❌ {right_answer}/{amount}")
        data['score'] = msg.message_id
        await state.update_data(test=data)

        await play(user_id, callback.from_user.first_name, state, bot=bot)


async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await bot.set_my_commands(commands=private, scope=types.BotCommandScopeAllPrivateChats())
    await dp.start_polling(bot,
                           allowed_updates=["message", "edited_message", "callback_query", "inline_query"],
                           polling_timeout=20)


if __name__ == '__main__':
    asyncio.run(main())
