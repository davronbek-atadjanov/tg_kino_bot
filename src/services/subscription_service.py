"""
Kanalga obuna tekshirish
"""
from aiogram import Bot
from aiogram.exceptions import TelegramAPIError
from src.config import settings


class SubscriptionService:
    """Obuna tekshirish servisi"""
    
    @staticmethod
    async def check_subscription(bot: Bot, user_id: int) -> bool:
        """Barcha kanallarga obuna bo'lganini tekshirish"""
        try:
            for channel_id in settings.SUBSCRIPTION_CHANNELS:
                try:
                    member = await bot.get_chat_member(channel_id, user_id)
                    # Agar user chiqib ketgan bo'lsa
                    if member.status == "left":
                        return False
                except TelegramAPIError:
                    return False
            return True
        except Exception:
            return False
    
    @staticmethod
    async def check_single_subscription(bot: Bot, user_id: int, channel_id: int) -> bool:
        """Bitta kanalga obuna tekshirish"""
        try:
            member = await bot.get_chat_member(channel_id, user_id)
            return member.status != "left"
        except TelegramAPIError:
            return False
