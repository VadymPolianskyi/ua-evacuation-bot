import logging

from src.config import msg, marker, limits
from src.handler import TelegramCallbackHandler, CallbackMeta
from src.service import markup
from src.service.message_separator import separate
from src.service.user import UserService


class BlackListCallbackHandler(TelegramCallbackHandler):
    MARKER = marker.BLACK_LIST

    def __init__(self, user_service: UserService):
        TelegramCallbackHandler.__init__(self)
        self.user_service = user_service

    async def handle_(self, callback: CallbackMeta):
        logging.info(f"BlackListCallbackHandler.handle for User({callback.user_id})")

        black_list = [f"{i + 1}. {u.to_str()}" for i, u in enumerate(self.user_service.black_list())]
        logging.info(f"Black list length - {len(black_list)}")

        black_list_str: str = "\n" + "\n\n".join(black_list)

        final_message = msg.BLACK_LIST_RESULT.format(black_list_str)
        reply_markup = markup.create_inline_markup_([(msg.BACK_BUTTON, marker.FIND, '_')])
        logging.info(f"BlackListCallbackHandler Final message: {final_message}")

        if len(final_message) > limits.FIND_RESPONSE_LIMIT:
            logging.info(f"Response more messages becaulse of text length = {len(final_message)}")
            separated = separate(final_message)
            for m in separated:
                if separated.index(m) == len(separated) - 1:
                    await callback.original.message.answer(m, reply_markup=reply_markup, disable_web_page_preview=True)
                else:
                    m = m if len(m) > 0 else msg.ADDITIONAL
                    await callback.original.message.answer(m, disable_web_page_preview=True)
        else:
            await callback.original.message.answer(final_message, reply_markup=reply_markup,
                                                   disable_web_page_preview=True)
