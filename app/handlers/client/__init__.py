from aiogram import Router
from .depart import depart_router
from .parcel import parcel_router
from .order_type import order_type_router

client_router = Router(name="client")
client_router.include_router(order_type_router)
client_router.include_router(depart_router)
client_router.include_router(parcel_router)