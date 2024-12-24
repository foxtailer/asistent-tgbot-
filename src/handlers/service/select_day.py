from aiogram import  types, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from ...states.user_states import UserState
from ...services import db_functions


select_day_router = Router()


@select_day_router.message(Command("select_day"))
async def select_day(msg: types.Message, command, state: FSMContext):
    await state.set_state(UserState.day)
    
    if command.args and command.args.strip().isdigit():
        day = await db_functions.get_day(msg.from_user.first_name,  (int(command.args),))
       
        if day:
            await state.update_data(day={'days': day})
        else:
           await msg.answer("Wrong day numder!")
    else:
        await msg.answer(f"Pls tipe number of day you want to select after command.\n\n"
                            "<code>/select_day 3</code>\n\n"
                            "You can finde day number using <code>/show</code> command.")
        
    await msg.delete()
