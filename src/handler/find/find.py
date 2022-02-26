from aiogram.types import Message

from src.config import marker, msg
from src.handler.general import TelegramCallbackHandler, CallbackMeta
from src.service import markup


class FindGeneral:

    async def _show_find_menu(self, message: Message):
        menu_keyboard = markup.create_inline_markup_([
            (msg.FIND_HOME_BUTTON, marker.FIND_HOME, '_'),
            (msg.FIND_TRIP_BUTTON, marker.FIND_TRIP, '_'),
            (msg.BACK_BUTTON, marker.MENU, '_')
        ])

        await message.answer(msg.FIND, reply_markup=menu_keyboard, disable_web_page_preview=True)


class FindCallbackHandler(TelegramCallbackHandler, FindGeneral):
    MARKER = marker.FIND

    def __init__(self):
        TelegramCallbackHandler.__init__(self)
        FindGeneral.__init__(self)

    async def handle_(self, callback: CallbackMeta):
        await self._show_find_menu(callback.original.message)
