"""
Obuna bilan bog'liq handlers
"""
from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.filters import Command
from aiogram.types import Message
from src.services.subscription_service import SubscriptionService
from src.utils.constants import Text, get_subscribe_keyboard

router = Router()


@router.callback_query(F.data == "check_subscription")
async def check_subscription_handler(callback: CallbackQuery):
    """Obunani tekshirish"""
    is_subscribed = await SubscriptionService.check_subscription(
        callback.bot,
        callback.from_user.id
    )
    
    if is_subscribed:
        await callback.answer(Text.SUBSCRIBE_SUCCESS, show_alert=True)
        await callback.message.delete()
    else:
        await callback.answer("⛔ Siz hali kanallarga obuna bo'lmadingiz!", show_alert=True)
        await callback.message.edit_text(
            Text.SUBSCRIBE_REQUIRED,
            reply_markup=get_subscribe_keyboard()
        )
