import logging
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from src.database.session import get_session
from src.services.movie_service import MovieService
from src.services.user_service import UserService
from src.utils.constants import Text, UserKeyboard, AdminKeyboard
from src.middleware.subscription_check import SubscriptionCheckMiddleware

router = Router()
logger = logging.getLogger(__name__)


class UserStates(StatesGroup):
    """User FSM States"""
    waiting_for_code = State()

@router.message(F.text == "📝 Kino kodi kiriting")
async def enter_code_button_handler(message: Message, state: FSMContext):
    """Kino kodi kiriting tugmasini bosganda"""
    logger.info(f"User tapped '📝 Kino kodi kiriting' button - ID: {message.from_user.id}")
    
    await message.answer(
        Text.ENTER_CODE,
    )
    await state.set_state(UserStates.waiting_for_code)

@router.message(UserStates.waiting_for_code)
async def code_handler(message: Message, state: FSMContext):
    """
    ✅ Kino kodi qabul qilib kino yuborish
    YANGILANGAN VERSION
    """
    
    # Raqam o'zgarishini tekshirish
    try:
        code = int(message.text)
    except ValueError:
        await message.answer(Text.INVALID_CODE_FORMAT)
        await message.answer(Text.ENTER_CODE)
        return
    
    logger.info(f"User entered code: {code} - ID: {message.from_user.id}")
    
    # Kino databasedan izlash
    async with get_session() as session:
        movie = await MovieService.get_by_code(session, code)
        
        if movie:
            # ✅ KINO TOPILDI - VIDEO + CAPTION YUBORISH
            message_identifier = movie.message_id

            try:
                # message_identifier may be either a file_id or a stored "<chat_id>:<message_id>"
                if message_identifier and ":" in message_identifier:
                    # copy from original chat (useful for forwarded posts from channels)
                    parts = message_identifier.split(":", 1)
                    from_chat_id = int(parts[0])
                    from_message_id = int(parts[1])
                    await message.bot.copy_message(
                        chat_id=message.chat.id,
                        from_chat_id=from_chat_id,
                        message_id=from_message_id,
                        caption=movie.caption or "📽️ Kino"
                    )
                else:
                    # treat as file_id
                    await message.bot.send_video(
                        chat_id=message.chat.id,
                        video=message_identifier,
                        caption=movie.caption or "📽️ Kino"
                    )

                logger.info(f"Video sent successfully - Code: {code}")

                # Main menyu ko'rsatish
                await message.answer(
                    "🏠 Asosiy Menu",
                    reply_markup=UserKeyboard.get_main_keyboard()
                )

            except Exception as e:
                logger.error(f"Error sending video - Code: {code}, Error: {str(e)}")
                await message.answer(
                    f"❌ Video yuborishda xato: {str(e)}\n\n"
                    f"Iltimos, adminga xabar bering."
                )
        else:
            # ❌ KINO TOPILMADI
            logger.warning(f"Movie not found - Code: {code}")
            await message.answer(Text.CODE_NOT_FOUND)
            await message.answer(Text.ENTER_CODE)