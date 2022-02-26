from src.config import marker, msg
from src.handler.general import TelegramCallbackHandler, CallbackMeta
from src.service import markup


class InfoCallbackHandler(TelegramCallbackHandler):
    MARKER = marker.INFO

    def __init__(self):
        TelegramCallbackHandler.__init__(self)

    async def handle_(self, callback: CallbackMeta):
        menu_keyboard = markup.create_inline_markup_([
            (msg.BACK_BUTTON, marker.MENU, '_')
        ])

        await callback.original.message.answer(msg.INFO, reply_markup=menu_keyboard, disable_web_page_preview=True)
