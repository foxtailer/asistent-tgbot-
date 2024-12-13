from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup


class UserState(StatesGroup):
    shuffle = State()
    show = State()
    test = State()
    write = State()
