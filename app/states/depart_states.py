from aiogram.fsm.state import StatesGroup, State

class OrderState(StatesGroup):
    choose_for_whom = State()
    choose_order_type = State()
    choose_from_viloyat = State()
    choose_from_tuman = State()
    choose_to_viloyat = State()
    choose_to_tuman = State()
    choose_time = State()
    choose_phone = State()
    choose_location = State()
    choose_comment = State()
    confirm = State()