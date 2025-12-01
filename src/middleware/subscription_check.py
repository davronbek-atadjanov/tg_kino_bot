import logging
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from typing import Callable, Any, Awaitable, Union

from src.services.subscription_service import SubscriptionService
from src.utils.constants import Text, UserKeyboard
from src.config import settings

logger = logging.getLogger(__name__)


class SubscriptionCheckMiddleware(BaseMiddleware):
    """Obuna tekshirish middleware - message va callback query uchun"""
    
    # Admin callback larni skip qilish
    ADMIN_CALLBACKS = {
        "add_movie", 
        "delete_movie", 
        "list_movies", 
        "cancel",
        "check_subscription"
    }
    
    # Admin komandalarni skip qilish
    ADMIN_COMMANDS = {"/admin", "/stats"}
    
    # Obunasizlar uchun ruxsat berilgan komandalar
    PUBLIC_COMMANDS = {"/start", "/help", "/myinfo"}
    
    async def __call__(
        self,
        handler: Callable[[Union[Message, CallbackQuery], dict[str, Any]], Awaitable[Any]],
        event: Union[Message, CallbackQuery],
        data: dict[str, Any],
    ) -> Any:
        """Middleware logic"""
        
        user = event.from_user
        user_id = user.id if user else None
        
        # Admin uchun middleware skip qilish
        if user_id is not None and SubscriptionCheckMiddleware._is_admin(user_id):
            logger.info(f"Admin {user_id} bypass middleware")
            return await handler(event, data)
        
        # Callback query uchun
        if isinstance(event, CallbackQuery):
            # Admin callback larni skip qilish
            if event.data in self.ADMIN_CALLBACKS:
                return await handler(event, data)
            
        #     # Callback query da obunani tekshirish
        #     # is_subscribed = await SubscriptionService.check_subscription(
        #     #     data.get("bot"), 
        #     #     user_id
        #     # )
        #     # print(f"Callback query uchun obuna tekshirish natijasi: {is_subscribed}")
            
        #     if not is_subscribed:
        #         logger.warning(f"Obunasiz user {user_id} callback query {event.data} yubordi")
        #         await event.answer(
        #             "⛔ Avval kanallarga obuna bo'lishingiz kerak!",
        #             show_alert=True
        #         )
            return
        
        # Message uchun
        elif isinstance(event, Message):
            # Komanda tekshirish
            if event.text and event.text.startswith("/"):
                command = event.text.split()[0]
                
                # Public komandalar - obunasiz ham ishlatishi mumkin
                if command in self.PUBLIC_COMMANDS:
                    return await handler(event, data)
                
                # Admin komandalar - faqat admin
                if command in self.ADMIN_COMMANDS:
                    return await handler(event, data)
            
            # # Obunani tekshirish
            # is_subscribed = await SubscriptionService.check_subscription(
            #     data.get("bot"), 
            #     user_id
            # )
            # logger.info(f"query uchun obuna tekshirish natijasi: {is_subscribed}")
            
            # if not is_subscribed:
            #     logger.warning(f"Obunasiz user {user_id} message yubordi: {event.text}")
            #     await event.answer(
            #         Text.SUBSCRIBE_REQUIRED,
            #         reply_markup=UserKeyboard.get_subscribe_keyboard()
            #     )
                return
        
        # Obunali user - handler ishga tushirish
        return await handler(event, data)
    
    @staticmethod
    def _is_admin(user_id: int) -> bool:
        """Admin tekshirish"""
        return user_id in settings.ADMINS
