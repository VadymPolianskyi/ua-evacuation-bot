import logging

from src.config import msg, marker, limits
from src.db.entity import AnnouncementType, AnnouncementServiceType
from src.handler import TelegramCallbackHandler, CallbackMeta
from src.handler.my import DeleteAnnouncementBeforeVoteCallbackHandler
from src.service import markup, file_service
from src.service.announcement import AnnouncementService


class FindMyAnnouncementsCallbackHandler(TelegramCallbackHandler):
    MARKER = marker.FIND_MY

    def __init__(self, announcement_service: AnnouncementService):
        TelegramCallbackHandler.__init__(self)
        self.announcement_service = announcement_service

    async def handle_(self, callback: CallbackMeta):
        logging.info(f"FindMyAnnouncementsCallbackHandler.handle for User({callback.user_id})")

        user_announcements = self.announcement_service.find_by_user(callback.user_id, AnnouncementType.find)

        buttons = list()
        announcements = list()
        logging.info(f"Create buttons for User({callback.user_id}) 'FIND_MY' menu")
        for i, a in enumerate(user_announcements):
            i = i + 1
            button_name = f'{msg.DELETE_SIGN} {i}. {a.a_service.value} - {a.city()}'
            element = (button_name, DeleteAnnouncementBeforeVoteCallbackHandler.MARKER, a.id)
            buttons.append(element)
            announcements.append(f"{i}. {a.to_str()}")

        logging.info("Buttons 'FIND_MY' menu created")
        buttons.append((msg.BACK_BUTTON, marker.FIND, '_'))

        announcements_str: str = "\n" + "\n\n".join(announcements)

        final_message = msg.FIND_MY.format(announcements_str)
        logging.info(f"FindMyAnnouncementsCallbackHandler Final message: {final_message}")

        if len(final_message) > limits.FIND_RESPONSE_LIMIT:
            logging.info(f"Response file becaulse of text length = {len(final_message)}")
            f = file_service.create_text_file(final_message, AnnouncementServiceType.home.value, callback.user_id)
            await callback.original.message.answer_document(f)
            file_service.close(f)
        else:
            await callback.original.message.answer(final_message, reply_markup=markup.create_inline_markup_(buttons))
