import logging
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from src.database.session import get_session
from src.services.user_service import UserService
from src.utils.constants import Text, UserKeyboard, AdminKeyboard
from src.routers.user import UserStates, code_handler
from src.middleware.subscription_check import SubscriptionCheckMiddleware

router = Router()
logger = logging.getLogger(__name__)


@router.message(Command("start"))
async def start_handler(message: Message, state: FSMContext):
    """Start kommandasi - Foydalanuvchini yaratish va xush kelibsiz matn"""
    async with get_session() as session:
        # Foydalanuvchini database ga qo'shish
        user = await UserService.get_or_create(session, message.from_user.id)
    
    logger.info(f"User started bot - ID: {message.from_user.id}")
    
    if user.user_type in ["owner", "admin"]:
        # Admin uchun xush kelibsiz matn
        await message.answer(
            Text.WELCOME_ADMIN,
            reply_markup=AdminKeyboard.get_main_keyboard()
        )
        return
    else:
        await message.answer(
            Text.WELCOME_USER,
            reply_markup=UserKeyboard.get_main_keyboard()
        )
        
        # # Obuna tugmalari
        # await message.answer(
        #     Text.SUBSCRIBE_REQUIRED,
        #     reply_markup=UserKeyboard.get_subscribe_keyboard()
        # )
        
        # Kino kodini kiritish uchun state belgilash
        await state.set_state(UserStates.waiting_for_code)
        return