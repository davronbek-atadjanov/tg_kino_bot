"""
Constants va klaviaturalar
"""
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from src.config import settings


class Text:
    """Matnlar"""
    WELCOME = """
👋 Assalomu alaikum! Kino Bot ga xush kelibsiz!

Kino kodini kiritib, uning linkini oling.

⚠️ Oldin kanallarga obuna bo'lishingiz kerak.
"""
    
    ENTER_CODE = "🎬 Kino kodini kiriting:"
    CODE_NOT_FOUND = "❌ Bunday kod mavjud emas"
    MOVIE_FOUND = "✅ Mana sizning kiningiz:\n\n"
    
    SUBSCRIBE_REQUIRED = "⛔ Iltimos, barcha kanallarga obuna bo'ling:"
    SUBSCRIBE_SUCCESS = "✅ Obunani tekshirganingiz uchun raxmat!"
    
    # Admin
    ADMIN_MENU = """
🔐 Admin Paneli

Kerakli amallarni tanlang:
"""
    ADD_MOVIE = "Kino qo'shish uchun:\n1️⃣ Kino kodini kiriting\n2️⃣ URL linkini kiriting"
    ENTER_MOVIE_CODE = "📝 Kino kodini kiriting (raqam):"
    ENTER_MOVIE_URL = "🔗 Kino URL linkini kiriting:"
    MOVIE_ADDED = "✅ Kino qo'shildi!\n\nKod: {code}\nURL: {url}"
    DELETE_MOVIE = "❌ O'chirish uchun kino kodini kiriting:"
    MOVIE_DELETED = "✅ Kino o'chirildi! (Kod: {code})"
    MOVIE_DELETE_FAILED = "❌ Shu kodli kino topilmadi"
    
    ALL_MOVIES = "📽️ Barcha kinolar:\n\n"
    NO_MOVIES = "📽️ Hozircha kinolar yo'q"


def get_subscribe_keyboard() -> InlineKeyboardMarkup:
    """Obuna bo'lish tugmalari"""
    builder = InlineKeyboardBuilder()
    
    channels_info = {}
    
    # Kanal mavjud bo'lsa qo'shish
    if len(settings.SUBSCRIPTION_CHANNELS) > 0:
        channels_info[settings.SUBSCRIPTION_CHANNELS[0]] = "📺 Kanal 1"
    if len(settings.SUBSCRIPTION_CHANNELS) > 1:
        channels_info[settings.SUBSCRIPTION_CHANNELS[1]] = "📺 Kanal 2"
    if len(settings.SUBSCRIPTION_CHANNELS) > 2:
        channels_info[settings.SUBSCRIPTION_CHANNELS[2]] = "📺 Kanal 3"
    
    # Tugmalar yaratish
    for channel_id, name in channels_info.items():
        builder.button(
            text=f"➕ {name}",
            url=f"https://t.me/c/{str(channel_id)[4:]}"  # Private channel
        )
    
    builder.button(text="✅ Tekshirish", callback_data="check_subscription")
    builder.adjust(1)
    
    return builder.as_markup()



def get_admin_keyboard() -> InlineKeyboardMarkup:
    """Admin menu tugmalari"""
    builder = InlineKeyboardBuilder()
    
    builder.button(text="➕ Kino qo'shish", callback_data="add_movie")
    builder.button(text="➖ Kino o'chirish", callback_data="delete_movie")
    builder.button(text="📽️ Ro'yxat", callback_data="list_movies")
    builder.button(text="❌ Bekor", callback_data="cancel")
    
    builder.adjust(1)
    return builder.as_markup()


def get_cancel_keyboard() -> InlineKeyboardMarkup:
    """Bekor tugmasi"""
    builder = InlineKeyboardBuilder()
    builder.button(text="❌ Bekor", callback_data="cancel")
    return builder.as_markup()
