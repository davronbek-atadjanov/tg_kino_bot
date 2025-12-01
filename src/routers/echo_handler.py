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


@router.message()
async def echo_handler(message: Message, state: FSMContext):
    """
    Aniqlanmagan xabarlar
    Agar state waiting_for_code bo'lsa, code handler ga o'tkazish
    """
    current_state = await state.get_state()
    
    if current_state == UserStates.waiting_for_code:
        # Agar kino kodi kutilayotgan bo'lsa, handleriga o'tkazish
        
        await code_handler(message, state)
    else:
        # User type check
        is_admin = SubscriptionCheckMiddleware._is_admin(message.chat.id)
        if is_admin:
            await message.answer(
                "❓ Admin panelda bunda command mavjud emas.\n\n"
                "Iltimos, admin menyu tugmalaridan birini tanlang.",        
                reply_markup=AdminKeyboard.get_main_keyboard()      
            )
        else:
            await message.answer(
                "❓ Men bu xabarni tushunmadim.\n\n"
                "Iltimos, asosiy menyu tugmalaridan birini tanlang.",
                reply_markup=UserKeyboard.get_main_keyboard()
            )

