
import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from src.config import settings
from src.database.session import get_session
from src.services.movie_service import MovieService
from src.services.user_service import UserService
from src.utils.constants import Text, AdminKeyboard

router = Router()
logger = logging.getLogger(__name__)


class AdminStates(StatesGroup):
    """Admin FSM States - YANGILANGAN"""
    waiting_for_movie_code = State()
    waiting_for_video = State()   
    waiting_for_caption = State() 
    waiting_for_delete_code = State()
    waiting_for_add_admin_id = State()
    waiting_for_remove_admin_id = State()


def is_admin(user_id: int) -> bool:
    """Admin tekshirish"""
    logger.info(f"Admin tekshirish: {user_id}")
    logger.info(f"Adminlar ro'yxati: {settings.ADMINS}")
    return user_id in settings.ADMINS


@router.message(Command("admin"))
async def admin_menu_handler(message: Message):
    """Admin menu - /admin komandasi"""
    if not is_admin(message.from_user.id):
        await message.answer(Text.ADMIN_ONLY)
        return
    
    await message.answer(
        Text.ADMIN_MENU,
        reply_markup=AdminKeyboard.get_main_keyboard()
    )

@router.message(F.text == "➕ Kino qo'shish")
async def add_movie_start(message: Message, state: FSMContext):
    """Kino qo'shish - boshlash (Step 1: Kod)"""
    if not is_admin(message.from_user.id):
        await message.answer(Text.ADMIN_ONLY, show_alert=True)
        return
    
    await message.answer(
        Text.ENTER_MOVIE_CODE,
        reply_markup=AdminKeyboard.get_cancel_keyboard()
    )
    await state.set_state(AdminStates.waiting_for_movie_code)


@router.message(AdminStates.waiting_for_movie_code)
async def movie_code_handler(message: Message, state: FSMContext):
    """
    Step 1: Kino kodi qabul qilish
    Kod raqam bo'lishi kerak (masalan: 123)
    """
    try:
        code = int(message.text)
    except ValueError:
        await message.answer(Text.INVALID_CODE_FORMAT)
        await message.answer(Text.ENTER_MOVIE_CODE)
        return
    
    # Kod allaqachon mavjud yoki yo'qligini tekshirish
    async with get_session() as session:
        exists = await MovieService.exists(session, code)
        if exists:
            await message.answer("❌ Bu kod allaqachon mavjud!")
            await message.answer(Text.ENTER_MOVIE_CODE)
            return
    
    # Kodni saqlash va keyingi qadamga o'tish
    await state.update_data(movie_code=code)
    await message.answer(
        Text.SEND_VIDEO,
        reply_markup=AdminKeyboard.get_cancel_keyboard()
    )
    await state.set_state(AdminStates.waiting_for_video)

@router.message(AdminStates.waiting_for_video)
async def kino_handler(message: Message, state: FSMContext):

    if not message.video:
        await message.answer("❌ Iltimos, video yuboring!")
        await message.answer(Text.SEND_VIDEO)
        return

    file_id = message.video.file_id

    # ⭐ CAPTION olish
    caption = message.caption or None

    # Determine message identifier to store:
    # - If message is forwarded from a channel, store as "<chat_id>:<message_id>"
    # - Otherwise store Telegram file_id so bot can send it later
    if getattr(message, "forward_from_chat", None) and getattr(message, "forward_from_message_id", None):
        orig_chat_id = message.forward_from_chat.id
        orig_message_id = message.forward_from_message_id
        message_identifier = f"{orig_chat_id}:{orig_message_id}"
    else:
        message_identifier = file_id

    # Save message identifier to state
    await state.update_data(message_id=message_identifier)

    if caption:
        # Agar video bilan caption kelsa — to'g'ridan-to'g'ri saqlaymiz
        data = await state.get_data()
        code = data.get("movie_code")

        async with get_session() as session:
            await MovieService.create(
                session,
                code=code,
                message_id=message_identifier,
                caption=caption
            )

        await message.answer(
            Text.MOVIE_ADDED.format(
                code=code,
                file_id=(message_identifier[:30] + "...") if message_identifier else "",
                caption=caption[:50]
            ),
            reply_markup=AdminKeyboard.get_main_keyboard()
        )

        await state.clear()
        return

    # Agar caption yo‘q bo‘lsa — keyingi qadamga o‘tamiz (caption so‘raymiz)
    await message.answer(
        Text.ENTER_CAPTION,
        reply_markup=AdminKeyboard.get_skip_keyboard()
    )
    await state.set_state(AdminStates.waiting_for_caption)


@router.callback_query(F.data == "⏭️ Skip")
async def skip_caption_handler(callback: CallbackQuery, state: FSMContext):
    """
    Caption qismi - SKIP (o'tkazib yuborish)
    Caption siz caption qo'llanish
    """
    await callback.answer()
    
    # Data olish
    data = await state.get_data()
    code = data.get("movie_code")
    message_identifier = data.get("message_id")
    
    logger.info(f"Caption skipped for movie code: {code}")
    
    # Database ga saqlash (caption = None)
    async with get_session() as session:
        await MovieService.create(session, code, message_identifier, caption=None)
    
    # Success message
    await callback.message.edit_text(
        Text.CAPTION_SKIPPED,
    )
    
    await callback.message.answer(
        Text.MOVIE_ADDED.format(
            code=code,
            file_id=(message_identifier[:30] + "...") if message_identifier else "",
            caption="Yo'q"
        ),
        reply_markup=AdminKeyboard.get_main_keyboard()
    )
    
    await state.clear()


@router.message(AdminStates.waiting_for_caption)
async def caption_handler(message: Message, state: FSMContext):
    """
    Step 3: Caption qabul qilish va videoni bazaga saqlash
    Caption - video tavsifi (masalan: "Rambo - aksiyoni filmi")
    """
    caption = message.text
    
    # Data olish (code va file_id)
    data = await state.get_data()
    code = data.get("movie_code")
    message_identifier = data.get("message_id")
    
    logger.info(f"Video added - Code: {code}, Caption: {caption[:50]}")
    
    # ✅ DATABASE GA SAQLASH (FILE_ID + CAPTION)
    async with get_session() as session:
        await MovieService.create(
            session,
            code,
            message_identifier,
            caption=caption
        )
    
    # Success message
    await message.answer(
        Text.MOVIE_ADDED.format(
            code=code,
            file_id=(message_identifier[:30] + "...") if message_identifier else "",
            caption=caption[:50] + ("..." if len(caption) > 50 else "")
        ),
        reply_markup=AdminKeyboard.get_main_keyboard()
    )
    
    # State clear
    await state.clear()


@router.message(F.text == "➖ Kino o'chirish")
async def delete_movie_start(message: Message, state: FSMContext):
    """Kino o'chirish - boshlash"""
    if not is_admin(message.from_user.id):
        await message.answer(Text.ADMIN_ONLY, show_alert=True)
        return
    
    await message.answer(
        Text.DELETE_MOVIE,
        reply_markup=AdminKeyboard.get_cancel_keyboard()
    )
    await state.set_state(AdminStates.waiting_for_delete_code)


@router.message(AdminStates.waiting_for_delete_code)
async def delete_movie_handler(message: Message, state: FSMContext):
    """Kino o'chirish"""
    try:
        code = int(message.text)
    except ValueError:
        await message.answer(Text.INVALID_CODE_FORMAT)
        await message.answer(Text.DELETE_MOVIE)
        return
    
    async with get_session() as session:
        success = await MovieService.delete(session, code)
    
    if success:
        logger.info(f"Movie deleted - Code: {code}")
        await message.answer(
            Text.MOVIE_DELETED.format(code=code),
            reply_markup=AdminKeyboard.get_main_keyboard()
        )
    else:
        await message.answer(
            Text.MOVIE_DELETE_FAILED,
            reply_markup=AdminKeyboard.get_main_keyboard()
        )
    
    await state.clear()


@router.message(F.text == "❌ Bekor")
async def cancel_handler(message: Message, state: FSMContext):
    """Amallarni bekor qilish"""
    await state.clear()
    await message.answer(
        Text.ADMIN_MENU,
        reply_markup=AdminKeyboard.get_main_keyboard()
    )


@router.message(F.text == "📊 Statistika")
async def stats_handler(message: Message):
    """Admin statistika"""
    if not is_admin(message.from_user.id):
        await message.answer(Text.ADMIN_ONLY)
        return
    
    async with get_session() as session:
        movies = await MovieService.get_all(session)
        count_users = await UserService.count_users(session)
    
    stats_text = f"""
📊 Bot Statistika

📽️ Jami kinolar: {len(movies)}

👥 Ro'yxatdan o'tkan foydalanuvchilar soni {count_users} 
    """
    
    await message.answer(stats_text)


# ========== ADMIN MANAGEMENT HANDLERS ==========

@router.message(F.text == "👥 Adminlar")
async def admin_management_handler(message: Message):
    """Admin boshqarish menyusu"""
    if not is_admin(message.from_user.id):
        await message.answer(Text.ADMIN_ONLY)
        return
    
    await message.answer(
        Text.ADMIN_MANAGEMENT,
        reply_markup=AdminKeyboard.get_admin_management_keyboard()
    )


@router.message(F.text == "📋 Adminlar ro'yxati")
async def list_admins_handler(message: Message):
    """Adminlar ro'yxatini ko'rsatish"""
    if not is_admin(message.from_user.id):
        await message.answer(Text.ADMIN_ONLY)
        return
    
    async with get_session() as session:
        # Barcha adminlarni database'dan olish
        from sqlalchemy import select
        from src.database.models import User, UserType
        
        stmt = select(User).where(User.user_type == UserType.ADMIN or User.user_type == UserType.OWNER)
        result = await session.execute(stmt)
        admins = result.scalars().all()
        
        if not admins:
            await message.answer(Text.NO_ADMINS)
        else:
            admin_list = Text.ADMIN_LIST
            for admin in admins:
                admin_list += f"👤 ID: `{admin.telegram_id}`\n"
            
            await message.answer(admin_list, parse_mode="Markdown")
    
    await message.answer(
        "🔧 Kerakli amallarni tanlang:",
        reply_markup=AdminKeyboard.get_admin_management_keyboard()
    )


@router.message(F.text == "➕ Admin qo'shish")
async def add_admin_start(message: Message, state: FSMContext):
    """Admin qo'shishni boshlash"""
    if not is_admin(message.from_user.id):
        await message.answer(Text.ADMIN_ONLY)
        return
    
    await message.answer(Text.ADD_ADMIN_PROMPT)
    await state.set_state(AdminStates.waiting_for_add_admin_id)


@router.message(AdminStates.waiting_for_add_admin_id)
async def add_admin_handler(message: Message, state: FSMContext):
    """Admin ID qabul qilish va qo'shish"""
    try:
        user_id = int(message.text)
    except ValueError:
        await message.answer("❌ Iltimos, faqat raqam kiriting!")
        await message.answer(Text.ADD_ADMIN_PROMPT)
        return
    
    async with get_session() as session:
        # User ni database'dan izlash yoki yaratish
        from src.database.models import UserType
        user = await UserService.get_or_create(session, user_id)
        
        if user.user_type == UserType.ADMIN:
            await message.answer(Text.ADMIN_ALREADY_EXISTS.format(user_id=user_id))
        else:
            user.user_type = UserType.ADMIN
            await session.flush()
            logger.info(f"Admin added: {user_id} by {message.from_user.id}")
            await message.answer(Text.ADMIN_ADDED.format(user_id=user_id))
    
    await message.answer(
        "🔧 Kerakli amallarni tanlang:",
        reply_markup=AdminKeyboard.get_admin_management_keyboard()
    )
    await state.clear()


@router.message(F.text == "➖ Admin o'chirish")
async def remove_admin_start(message: Message, state: FSMContext):
    """Admin o'chirishni boshlash"""
    if not is_admin(message.from_user.id):
        await message.answer(Text.ADMIN_ONLY)
        return
    
    await message.answer(Text.REMOVE_ADMIN_PROMPT)
    await state.set_state(AdminStates.waiting_for_remove_admin_id)


@router.message(AdminStates.waiting_for_remove_admin_id)
async def remove_admin_handler(message: Message, state: FSMContext):
    """Admin ID qabul qilish va o'chirish"""
    try:
        user_id = int(message.text)
    except ValueError:
        await message.answer("❌ Iltimos, faqat raqam kiriting!")
        await message.answer(Text.REMOVE_ADMIN_PROMPT)
        return
    
    async with get_session() as session:
        from src.database.models import UserType
        user = await UserService.get_or_create(session, user_id)
        
        if user.user_type != UserType.ADMIN:
            await message.answer(Text.ADMIN_NOT_FOUND.format(user_id=user_id))
        else:
            user.user_type = UserType.USER
            await session.flush()
            logger.info(f"Admin removed: {user_id} by {message.from_user.id}")
            await message.answer(Text.ADMIN_REMOVED.format(user_id=user_id))
    
    await message.answer(
        "🔧 Kerakli amallarni tanlang:",
        reply_markup=AdminKeyboard.get_admin_management_keyboard()
    )
    await state.clear()


@router.message(F.text == "🔙 Orqaga")
async def back_to_admin_menu(message: Message, state: FSMContext):
    """Admin menyusiga qaytish"""
    await state.clear()
    await message.answer(
        Text.ADMIN_MENU,
        reply_markup=AdminKeyboard.get_main_keyboard()
    )