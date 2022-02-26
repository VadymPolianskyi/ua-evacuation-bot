from aiogram.types import Message

from src.config import marker, msg
from src.handler.general import TelegramCallbackHandler, CallbackMeta
from src.service import markup


class ShareGeneral:

    async def _show_share_menu(self, message: Message):
        menu_keyboard = markup.create_inline_markup_([
            (msg.SHARE_HOME_BUTTON, marker.SHARE_HOME, '_'),
            (msg.SHARE_TRIP_BUTTON, marker.SHARE_TRIP, '_'),
            (msg.BACK_BUTTON, marker.MENU, '_')
        ])

        await message.answer(msg.SHARE, reply_markup=menu_keyboard, disable_web_page_preview=True)


class ShareCallbackHandler(TelegramCallbackHandler, ShareGeneral):
    MARKER = marker.SHARE

    def __init__(self):
        TelegramCallbackHandler.__init__(self)
        ShareGeneral.__init__(self)

    async def handle_(self, callback: CallbackMeta):
        await self._show_share_menu(callback.original.message)
