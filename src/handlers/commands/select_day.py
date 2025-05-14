from aiogram import  types, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from ...states.user_states import UserState
from ...services import db_functions


select_day_router = Router()


@select_day_router.message(Command("select_day"))
async def select_day(msg: types.Message, command, state: FSMContext):
    """
    You can select day from your dictionary by:
    <code>/select_day [day]</code>
    Day can by a single number of day like 1 or 2
    <code>/select_day 1</code>
    It can be sequense of days separated by coma
    <code>/select_day 3,5,8</code>
    And it can by range of days
    <code>/select_day 3-6</code>
    """

    await state.clear()
    await state.set_state(UserState.day)
    
    if command.args and command.args.strip().isdigit():
        days = await db_functions.get_day(msg.from_user.first_name,  (int(command.args),))
       
        if days:
            await state.update_data(days={'days': days})  # dict[int:list[WordRow,]]
        else:
           await msg.answer("Wrong day numder!")
    else:
        await msg.answer(f"Pls tipe number of day you want to select after command.\n\n"
                            "<code>/select_day 3</code>\n\n"
                            "You can finde day number using <code>/show</code> command.")
        
    await msg.delete()
