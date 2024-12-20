from aiogram import  types, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from ...states.user_states import UserState

from ...services import db_functions


select_day_router = Router()


@select_day_router.message(Command("select_day"))
async def select_day(msg: types.Message, command, state: FSMContext):
    await state.set_state(UserState.test)

    if command.args and command.args.strip().isdigit():
        day = await db_functions.get_day(msg.from_user.first_name,  (int(command.args)-1,))
       
        if day:
            tmp = {'day': day, 'day_size': len(day), 'day_answers': 0}

            await state.update_data(test=tmp)
        else:
           await msg.answer(msg.chat.id, 
                                  "Wrong day numder!")
    else:
        await msg.answer(f"Pls tipe number of day you want to select after command.\n\n"
                            "<code>/select_day 3</code>\n\n"
                            "You can finde day number using <code>/show</code> command.")
        
    await msg.delete()