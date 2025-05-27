from aiogram import types, Router
from aiogram.fsm.context import FSMContext

from src.states.user_states import UserState
from src.handlers.commands.show_cmd import show_commmand


show_call_router = Router()


@show_call_router.callback_query(UserState.show)
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
