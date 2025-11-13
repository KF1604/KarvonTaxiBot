from aiogram.fsm.state import StatesGroup, State

class AdminManageState(StatesGroup):
    adding_user_id = State()
    adding_phone = State()
    choosing_role = State()
    confirming_add = State()

    removing_id = State()
    confirming_rm = State()

    role_change_id = State()
    role_change_choose = State()

    #------drivers------

    # ─── Haydovchi qo‘shish ────────────────────────
    adding_driver_id = State()  # 1. Haydovchi Telegram ID si
    adding_driver_phone = State()  # 2. Telefon raqamini kiritish
    adding_driver_car_model = State()  # ➕
    adding_driver_car_number = State()
    adding_driver_groups = State()  # 3. Guruh ID(lar)ni kiritish
    confirming_driver_add = State()  # 4. Qo‘shishni tasdiqlash

    # ─── Haydovchi o‘chirish ────────────────────────────
    removing_driver_id = State()  # 1. Haydovchi ID sini kiritish
    confirming_driver_rm = State()  # 2. O‘chirishni tasdiqlash

    # ─── Telefon raqamini tahrirlash ────────────────────
    editing_driver_id = State()  # 1. Tahrir qilinadigan haydovchi ID si
    editing_driver_phone = State()  # 2. Yangi telefon raqamini kiritish
    confirming_driver_phone_edit = State()  # 3. Tahrirni tasdiqlash

    # ─── Haydovchi mashinasini tahrirlash ────────────────────
    finding_driver_id_for_model = State()
    waiting_for_new_car_model = State()
    confirming_new_car_model=State()

    finding_driver_id_for_number = State()
    waiting_for_new_car_number = State()
    confirming_new_car_number = State()

    # ─── Guruh ID lar ───────────────────────────────────
    add_group_ids = State()  # 1. Haydovchi ID sini kiritish
    confirming_group_add_input = State()  # 2. Yangi guruh ID(lar)ni kiritish

    remove_group_ids = State()  # 1. Haydovchi ID sini kiritish
    confirming_group_remove_input = State()  # 2. O‘chiriladigan guruh ID(lar)ni kiritish
    finding_driver_id = State()

    #----Foydalanuvchilar----------

    finding_user = State()
    blocking_user = State()
    unblocking_user = State()
    deleting_user = State()
    messaging_user = State()
    messaging_user_text = State()
    replying_to_admin = State()
    admin_replying_user = State()

    # --- Reklama yuborish bosqichlari ---
    forward_ads = State()
    ads_confirm = State()

    #---Bot mode---
    confirming_switch = State()