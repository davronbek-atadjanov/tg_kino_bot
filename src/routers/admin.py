"""
Admin handlers - kino qo'shish, o'chirish, ro'yxat
"""
import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from src.config import settings
from src.database.session import get_session
from src.services.movie_service import MovieService
from src.services.user_service import UserService
from src.utils.constants import Text, get_admin_keyboard, get_cancel_keyboard

router = Router()

logger = logging.getLogger(__name__)



class AdminStates(StatesGroup):
    """Admin state machineları"""
    waiting_for_movie_code = State()
    waiting_for_movie_url = State()
    waiting_for_delete_code = State()


def is_admin(message: Message) -> bool:
    """Admin tekshirish decorator"""
    logger.info(f"Admin tekshirish: {message.from_user.id}")
    logger.info(f"Adminlar ro'yxati: {settings.ADMINS}, type: {type(settings.ADMINS)}")
    logger.info(f"Message: {message}")
    return message.chat.id in settings.ADMINS


@router.message(Command("admin"))
async def admin_menu_handler(message: Message):
    """Admin menu"""
    if not is_admin(message):
        await message.answer("❌ Siz admin emassiz!")
        return
    else:
        await message.answer(
            Text.ADMIN_MENU,
            reply_markup=get_admin_keyboard()
        )


@router.callback_query(F.data == "add_movie")
async def add_movie_start(callback: CallbackQuery, state: FSMContext):
    """Kino qo'shish - boshlash"""
    if not is_admin(callback.message):
        await callback.answer("❌ Siz admin emassiz!", show_alert=True)
        return
    else:
        await callback.message.edit_text(
            Text.ADD_MOVIE,
            reply_markup=get_cancel_keyboard()
        )
        await state.set_state(AdminStates.waiting_for_movie_code)
    


@router.message(AdminStates.waiting_for_movie_code)
async def movie_code_handler(message: Message, state: FSMContext):
    """Kino kodi qabul qilish"""
    try:
        code = int(message.text)
    except ValueError:
        await message.answer("❌ Iltimos, faqat raqam kiriting!")
        return
    
    async with get_session() as session:
        exists = await MovieService.exists(session, code)
        if exists:
            await message.answer("❌ Bu kod allaqachon mavjud!")
            return
    
    await state.update_data(movie_code=code)
    await message.answer(Text.ENTER_MOVIE_URL)
    await state.set_state(AdminStates.waiting_for_movie_url)


@router.message(AdminStates.waiting_for_movie_url)
async def movie_url_handler(message: Message, state: FSMContext):
    """Kino URL qabul qilish"""
    url = message.text
    data = await state.get_data()
    code = data.get("movie_code")
    
    async with get_session() as session:
        await MovieService.create(session, code, url)
    
    await message.answer(
        Text.MOVIE_ADDED.format(code=code, url=url)
    )
    await state.clear()


@router.callback_query(F.data == "delete_movie")
async def delete_movie_start(callback: CallbackQuery, state: FSMContext):
    """Kino o'chirish - boshlash"""
    if not is_admin(callback.message):
        await callback.answer("❌ Siz admin emassiz!", show_alert=True)
        return
    
    await callback.message.edit_text(
        Text.DELETE_MOVIE,
        reply_markup=get_cancel_keyboard()
    )
    await state.set_state(AdminStates.waiting_for_delete_code)


@router.message(AdminStates.waiting_for_delete_code)
async def delete_movie_handler(message: Message, state: FSMContext):
    """Kino o'chirish"""
    try:
        code = int(message.text)
    except ValueError:
        await message.answer("❌ Iltimos, faqat raqam kiriting!")
        return
    
    async with get_session() as session:
        success = await MovieService.delete(session, code)
    
    if success:
        await message.answer(Text.MOVIE_DELETED.format(code=code))
    else:
        await message.answer(Text.MOVIE_DELETE_FAILED)
    
    await state.clear()


@router.callback_query(F.data == "list_movies")
async def list_movies_handler(callback: CallbackQuery):
    """Kinolar ro'yxati"""
    if not is_admin(callback.message):
        await callback.answer("❌ Siz admin emassiz!", show_alert=True)
        return
    
    async with get_session() as session:
        movies = await MovieService.get_all(session)
    
    if not movies:
        text = Text.NO_MOVIES
    else:
        text = Text.ALL_MOVIES
        for i, movie in enumerate(movies, 1):
            text += f"{i}. Kod: {movie.code}\n   URL: {movie.url}\n\n"
    
    await callback.message.edit_text(text)


@router.callback_query(F.data == "cancel")
async def cancel_handler(callback: CallbackQuery, state: FSMContext):
    """Bekor qilish"""
    await state.clear()
    await callback.message.edit_text(
        Text.ADMIN_MENU,
        reply_markup=get_admin_keyboard()
    )

