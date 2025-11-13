from aiogram.fsm.state import StatesGroup, State

class ClickPaymentState(StatesGroup):
    waiting_for_payment = State()
    awaiting_confirmation = State()

class AccessStates(StatesGroup):
    send_all = State()

class PaymentDeleteState(StatesGroup):
    message_id = State()