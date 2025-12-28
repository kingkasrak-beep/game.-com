from aiogram.fsm.state import StatesGroup, State

class Register(StatesGroup):
    first_name = State()
    last_name = State()
    age = State()
    faction = State()
