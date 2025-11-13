from aiogram.fsm.state import State, StatesGroup

class DriverState(StatesGroup):
    selecting_depart_from = State()
    selecting_arrive_to = State()
    writing_announcement = State()

class DriverPhoneState(StatesGroup):
    editing_phone = State()
    confirming_phone = State()

class DriverAnnouncementState(StatesGroup):
    choosing_depart_from = State()
    choosing_arrive_to = State()
    writing_text = State()
    confirming = State()

class PhoneNumberState(StatesGroup):
    waiting_for_phone = State()
    editing_phone = State()

class AdminAnnouncementStates(StatesGroup):
    waiting_driver_id = State()
    confirm_stop = State()
