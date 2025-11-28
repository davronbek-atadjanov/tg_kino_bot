"""
User handlers - kino kodini qabul qilish
"""
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from src.database.session import get_session
from src.services.movie_service import MovieService
from src.services.user_service import UserService
from src.utils.constants import Text

router = Router()


class UserStates(StatesGroup):
    """User state machineları"""
    waiting_for_code = State()


@router.message(Command("start"))
async def start_handler(message: Message, state: FSMContext):
    """Start kommandasi"""
    async with get_session() as session:
        await UserService.get_or_create(session, message.from_user.id)
    
    await message.answer(Text.WELCOME)
    await message.answer(Text.ENTER_CODE)
    await state.set_state(UserStates.waiting_for_code)


@router.message(UserStates.waiting_for_code)
async def code_handler(message: Message, state: FSMContext):
    """Kino kodi qabul qilish"""
    try:
        code = int(message.text)
    except ValueError:
        await message.answer("❌ Iltimos, faqat raqam kiriting!")
        return
    
    async with get_session() as session:
        movie = await MovieService.get_by_code(session, code)
        
        if movie:
            await message.answer(
                f"{Text.MOVIE_FOUND}{movie.url}"
            )
        else:
            await message.answer(Text.CODE_NOT_FOUND)
    
    await message.answer(Text.ENTER_CODE)

