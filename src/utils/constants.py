from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from src.config import settings


class Text:
    """Barcha Bot Matnlari - YANGILANGAN"""
    
    # ========== USER MESSAGES ==========
    WELCOME_USER = """
👋 Assalomu alaikum! Kino Bot ga xush kelibsiz!

🎬 Kino kodini kiriting
"""
    WELCOME_ADMIN = """👋 Assalomu alaikum! Admin Panelga xush kelibsiz!"""
    
    ENTER_CODE = "🎬 Kino kodini kiriting:"
    CODE_NOT_FOUND = "❌ Bunday kod mavjud emas. Iltimos, yana urinib ko'ring."
    MOVIE_FOUND = "✅ Mana sizning kiningiz:\n\n"
    SUBSCRIBE_REQUIRED = "⛔ Iltimos, barcha kanallarga obuna bo'ling:"
    SUBSCRIBE_SUCCESS = "✅ Obunani tekshirganingiz uchun raxmat! Endi kino kodini kiritishingiz mumkin."
    INVALID_CODE_FORMAT = "❌ Iltimos, faqat raqam kiriting!"
    
    # ========== ADMIN MESSAGES ==========
    ADMIN_MENU = """
🔐 Admin Paneli

Kerakli amallarni tanlang:
    """
    
    # ✅ YANGILANGAN - VIDEO FILE_ID + CAPTION    
    ENTER_MOVIE_CODE = "📝 Kino kodini kiriting (faqat raqam):"
    
    # ✅ YANGILANGAN
    SEND_VIDEO = "🎥 Endi videoni shu chatga yuboring (forward qiling yoki upload qiling):"
    ENTER_CAPTION = "📝 Video caption/tavsifini kiriting (yoki skip tugmasini bosing):"
    
    # ✅ YANGILANGAN - FILE_ID va CAPTION ko'rsatish
    MOVIE_ADDED = "✅ Video qo'shildi!\n\n📝 Kod: {code}\n📹 Message ID: {file_id}\n📄 Caption: {caption}"
    
    DELETE_MOVIE = "❌ O'chirish uchun kino kodini kiriting:"
    MOVIE_DELETED = "✅ Video o'chirildi! (Kod: {code})"
    MOVIE_DELETE_FAILED = "❌ Shu kodli video topilmadi."
    
    ALL_MOVIES = "📽️ Barcha videolar:\n\n"
    NO_MOVIES = "📽️ Hozircha videolar yo'q."
    
    # ✅ YANGILANGAN
    CAPTION_SKIPPED = "⏭️ Caption o'tkazib yuborildi"

    CANCEL = "❌ Amal bekor qilindi."
    ADMIN_ONLY = "❌ Bu buyruq faqat adminlar uchun!"
    
    # ========== ADMIN MANAGEMENT ==========
    ADMIN_MANAGEMENT = """
👥 Admin Boshqarish

Kerakli amallarni tanlang:
    """
    
    ADMIN_LIST = "👥 Adminlar ro'yxati:\n\n"
    NO_ADMINS = "👥 Hozircha adminlar yo'q."
    
    ADD_ADMIN_PROMPT = "👤 Qo'shish uchun user ID kiriting:"
    ADMIN_ADDED = "✅ {user_id} admin sifatida qo'shildi!"
    ADMIN_ALREADY_EXISTS = "⚠️ {user_id} allaqachon admin!"
    
    REMOVE_ADMIN_PROMPT = "👤 O'chirish uchun user ID kiriting:"
    ADMIN_REMOVED = "✅ {user_id} admin ro'yxatidan o'chirildi!"
    ADMIN_NOT_FOUND = "❌ {user_id} admin emas!"



# ============================================================================
# USER KEYBOARD - REPLY KEYBOARD (Sizning kodni asosida)
# ============================================================================
class UserKeyboard:
    """User Klaviaturalar - REPLY KEYBOARD"""
    
    @staticmethod
    def get_main_keyboard() -> ReplyKeyboardMarkup:
        """User asosiy menyu - Reply Keyboard"""
        builder = ReplyKeyboardBuilder()
        
        builder.button(text="📝 Kino kodi kiriting")
        
        builder.adjust(1)  # 2 ta tugma bitta qatorda
        return builder.as_markup(
            resize_keyboard=True,
            one_time_keyboard=False
        )
    
    @staticmethod
    def get_subscribe_keyboard() -> InlineKeyboardMarkup:
        """Obuna bo'lish tugmalari - INLINE KEYBOARD"""
        builder = InlineKeyboardBuilder()
        
        # Kanallarga obuna tugmalari
        for idx, channel_id in enumerate(settings.SUBSCRIPTION_CHANNELS, 1):
            # Private channel URL format
            channel_username = str(channel_id)[4:]  # -100 dan keyin
            
            builder.button(
                text=f"📺 Kanal {idx}",
                url=f"https://t.me/c/{channel_username}"
            )
        
        # Tekshirish tugmasi
        builder.button(
            text="✅ Tekshirish",
            callback_data="check_subscription"
        )
        
        builder.adjust(1)  # Har tugma yangi qatorda
        return builder.as_markup()
    
    @staticmethod
    def get_cancel_keyboard() -> ReplyKeyboardMarkup:
        """Bekor tugmasi"""
        builder = ReplyKeyboardBuilder()
        builder.button(text="❌ Bekor")
        builder.adjust(1)
        return builder.as_markup(resize_keyboard=True)


# ============================================================================
# ADMIN KEYBOARD - INLINE KEYBOARD (YANGILANGAN)
# ============================================================================
class AdminKeyboard:
    """Admin Klaviaturalar - INLINE KEYBOARD - YANGILANGAN"""
    
    @staticmethod
    def get_main_keyboard() -> ReplyKeyboardMarkup:
        """Admin asosiy menyu - Inline Keyboard"""
        builder = ReplyKeyboardBuilder()
        
        builder.button(text="➕ Kino qo'shish")
        builder.button(text="➖ Kino o'chirish")
        builder.button(text="📊 Statistika")
        builder.button(text="👥 Adminlar")
        
        builder.adjust(2)  # 2 ta tugma bitta qatorda
        return builder.as_markup(
            resize_keyboard=True,
            one_time_keyboard=False
        )
    
    @staticmethod
    def get_cancel_keyboard() -> ReplyKeyboardMarkup:
        """Bekor tugmasi"""
        builder = ReplyKeyboardBuilder()
        builder.button(text="❌ Bekor")
        builder.adjust(1)
        return builder.as_markup(
            resize_keyboard=True
        )
    
    @staticmethod
    def get_skip_keyboard() -> ReplyKeyboardMarkup:
        """Caption o'tkazib yuborish tugmalari"""
        builder = ReplyKeyboardBuilder()
        builder.button(text="⏭️ Skip")
        builder.button(text="❌ Bekor")
        builder.adjust(1)
        return builder.as_markup(
            resize_keyboard=True
        )
    
    @staticmethod
    def get_admin_management_keyboard() -> ReplyKeyboardMarkup:
        """Admin boshqarish menyusu"""
        builder = ReplyKeyboardBuilder()
        builder.button(text="➕ Admin qo'shish")
        builder.button(text="➖ Admin o'chirish")
        builder.button(text="📋 Adminlar ro'yxati")
        builder.button(text="🔙 Orqaga")
        builder.adjust(2)
        return builder.as_markup(
            resize_keyboard=True,
            one_time_keyboard=False
        )


    