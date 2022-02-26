from aiogram.types import Message

from src.config import msg, marker
from src.handler.general import TelegramMessageHandler, MessageMeta, TelegramCallbackHandler, CallbackMeta
from src.service import markup


class MenuGeneral:

    async def _show_menu(self, original_message: Message, user_id: int = None):
        if not user_id:
            user_id = original_message.from_user.id

        menu_keyboard = markup.create_inline_markup_([
            (msg.FIND_BUTTON, marker.FIND, '_'),
            (msg.SHARE_BUTTON, marker.SHARE, '_'),
            (msg.MY_BUTTON, marker.MY, '_'),
            (msg.INFO_BUTTON, marker.INFO, '_')
        ])

        await original_message.answer(msg.MENU, reply_markup=menu_keyboard, disable_web_page_preview=True)


class MenuHandler(TelegramMessageHandler, MenuGeneral):
    def __init__(self):
        TelegramMessageHandler.__init__(self)
        MenuGeneral.__init__(self)

    async def handle_(self, message: MessageMeta, *args):
        await self._show_menu(message.original)


class MenuCallbackHandler(TelegramCallbackHandler, MenuGeneral):
    MARKER = marker.MENU

    def __init__(self):
        TelegramCallbackHandler.__init__(self)
        MenuGeneral.__init__(self)

    async def handle_(self, call: CallbackMeta):
        await self._show_menu(call.original.message, call.user_id)
