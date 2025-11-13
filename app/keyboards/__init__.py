# from .admin_inline import (
#     admin_menu_buttons,
#     admin_manage_buttons,
#     admin_role_buttons,
#     confirm_admin_button,
#     confirm_remove_button,
#     kb_main,
#     retry_back_buttons
# )
#
# from .depart_inline import (
#     start_menu_buttons,
#     order_type_buttons,
#     viloyat_buttons,
#     tuman_buttons,
#     confirm_keyboard,
#     to_main_menu_inline,
#     contact_client_button
# )
#
# from .depart_reply import (
#     phone_keyboard as depart_phone_keyboard,
#     location_keyboard as depart_location_keyboard,
#     comment_keyboard as depart_comment_keyboard,
#     cancel_reply_kb as depart_cancel_reply
# )
#
# from .parcel_inline import (
#     order_type_buttons as parcel_order_type_buttons,
#     viloyat_buttons as parcel_viloyat_buttons,
#     tuman_buttons as parcel_tuman_buttons,
#     confirm_keyboard as parcel_confirm_keyboard,
#     to_main_menu_inline as parcel_to_main_menu_inline,
#     contact_client_button as parcel_contact_client_button
# )
#
# from .parcel_reply import (
#     phone_keyboard as parcel_phone_keyboard,
#     location_keyboard as parcel_location_keyboard,
#     comment_keyboard as parcel_comment_keyboard,
#     cancel_reply_kb as parcel_cancel_reply
# )
#
# from .feedback_inline import (
#     user_reply_inline,
#     to_main_menu_inline as feedback_main_menu_inline,
#     admin_act_inline,
#     FB
# )
#
# from .feedback_reply import (
#     cancel_reply_kb as feedback_cancel_reply
# )
#
# from .admin_reply import (
#     cancel_reply_kb as admin_cancel_reply
# )



from . import (
    admin_inline,
    admin_reply,
    depart_inline,
    depart_reply,
    driver_inline,
    driver_reply,
    feedback_inline,
    feedback_reply,
    parcel_inline,
    parcel_reply,
)

from .parcel_inline import to_main_menu_inline  # <-- qo‘shildi

__all__ = [
    "admin_inline",
    "admin_reply",
    "depart_inline",
    "depart_reply",
    "driver_inline",
    "driver_reply",
    "feedback_inline",
    "feedback_reply",
    "parcel_inline",
    "parcel_reply",
    "to_main_menu_inline",  # <-- qo‘shildi
]

