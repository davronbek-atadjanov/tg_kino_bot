import logging
from typing import List
from aiogram import Bot
from aiogram.exceptions import TelegramAPIError

from src.config import settings

logger = logging.getLogger(__name__)


class SubscriptionService:
    """Kanallarga obunani tekshirish servisi"""
    
    @staticmethod
    async def check_subscription(bot: Bot, user_id: int) -> bool:
        """
        Foydalanuvchining barcha kanallarga obunasini tekshirish
        
        Args:
            bot: Aiogram Bot instance
            user_id: Telegram user ID
        
        Returns:
            bool: Barcha kanallarga obunali bo'lsa True
                  Subscription channels bo'sh bo'lsa True (obuna tekshirish o'chirilgan)
        """
        
        if not settings.SUBSCRIPTION_CHANNELS and len(settings.SUBSCRIPTION_CHANNELS) == 0:
            logger.info("Subscription channels bo'sh - obuna tekshirish o'chirilgan")
            return True
        
        else:
            for channel_id in settings.SUBSCRIPTION_CHANNELS:
                is_member = await SubscriptionService._check_member(bot, user_id, channel_id)
                
                if not is_member:
                    logger.info(f"Foydalanuvchi {user_id} kanal {channel_id} ga obunali emas")
                    return False
            
            return True 
    
    @staticmethod
    async def _check_member(bot: Bot, user_id: int, channel_id: int) -> bool:
        """
        Foydalanuvchining bitta kanalga obunasini tekshirish
        
        Args:
            bot: Aiogram Bot instance
            user_id: Telegram user ID
            channel_id: Kanal ID
        
        Returns:
            bool: Kanalga obunali bo'lsa True
        """
        try:
            member = await bot.get_chat_member(channel_id, user_id)
            
            # Obunali status larni tekshirish
            allowed_statuses = ["member", "administrator", "creator"]
            
            if member.status in allowed_statuses:
                return True
            
            return False
            
        except TelegramAPIError as e:
            logger.error(f"Obuna tekshirishda Telegram xatolik: {str(e)}")
            return False
