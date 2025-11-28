"""
Mandatory subscribe middleware
"""
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from typing import Callable, Any, Awaitable, Union
from src.services.subscription_service import SubscriptionService


class SubscriptionCheckMiddleware(BaseMiddleware):
    """Obuna tekshirish middleware - message va callback query uchun"""
    
    async def __call__(
        self,
        handler: Callable[[Union[Message, CallbackQuery], dict[str, Any]], Awaitable[Any]],
        event: Union[Message, CallbackQuery],
        data: dict[str, Any],
    ) -> Any:
        """Middleware logic"""
        
        # Callback query uchun
        if isinstance(event, CallbackQuery):
            # Admin callback larni skip qilish
            if event.data in ["add_movie", "delete_movie", "list_movies", "cancel", "check_subscription"]:
                return await handler(event, data)
        
        bot = data.get("bot")
        user_id = event.from_user.id if event.from_user else None
        
        # Obunani tekshirish
        is_subscribed = await SubscriptionService.check_subscription(bot, user_id)
        
        if not is_subscribed:
            from src.utils.constants import Text, get_subscribe_keyboard
            
            if isinstance(event, Message):
                await event.answer(
                    Text.SUBSCRIBE_REQUIRED,
                    reply_markup=get_subscribe_keyboard()
                )
            elif isinstance(event, CallbackQuery):
                await event.message.edit_text(
                    Text.SUBSCRIBE_REQUIRED,
                    reply_markup=get_subscribe_keyboard()
                )
            return
        
        return await handler(event, data)