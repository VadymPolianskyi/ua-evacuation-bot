import logging

from src.config import msg, marker, limits
from src.db.entity import AnnouncementType, AnnouncementServiceType
from src.handler.general import TelegramCallbackHandler, CallbackMeta
from src.handler.menu import MenuGeneral
from src.service import markup, file_service
from src.service.announcement import AnnouncementService
from src.service.markup import EMPTY_VOTE_RESULT


class MyAnnouncementsCallbackHandler(TelegramCallbackHandler):
    MARKER = marker.MY

    def __init__(self, announcement_service: AnnouncementService):
        TelegramCallbackHandler.__init__(self)
        self.announcement_service = announcement_service

    async def handle_(self, callback: CallbackMeta):
        logging.info(f"MyAnnouncementsCallbackHandler.handle for User({callback.user_id})")

        user_announcements = self.announcement_service.find_by_user(callback.user_id, AnnouncementType.share)

        logging.info(f"Found {len(user_announcements)} of User({callback.user_id})")

        buttons = list()
        announcements = list()
        logging.info(f"Create buttons for User({callback.user_id}) 'MY' menu")
        for i, a in enumerate(user_announcements):
            i = i + 1
            button_name = f'{msg.DELETE_SIGN} {i}. {a.a_service.value} - {a.city()}'
            element = (button_name, DeleteAnnouncementBeforeVoteCallbackHandler.MARKER, a.id)
            buttons.append(element)
            announcements.append(f"{i}. {a.to_str()}")

        logging.info("Buttons 'MY' menu created")
        buttons.append((msg.BACK_BUTTON, marker.MENU, '_'))

        announcements_str: str = "\n" + "\n\n".join(announcements)

        final_message = msg.MY.format(announcements_str)

        if len(final_message) > limits.FIND_RESPONSE_LIMIT:
            f = file_service.create_text_file(final_message, AnnouncementServiceType.home.value, callback.user_id)
            await callback.original.message.answer_document(f)
            file_service.close(f)
        else:
            await callback.original.message.answer(final_message, reply_markup=markup.create_inline_markup_(buttons))


class DeleteAnnouncementBeforeVoteCallbackHandler(TelegramCallbackHandler):
    MARKER = 'delanv'

    def __init__(self, announcement_service: AnnouncementService):
        super().__init__()
        self.announcement_service = announcement_service

    async def handle_(self, callback: CallbackMeta):
        logging.info(f"DeleteAnnouncementBeforeVoteCallbackHandler.handle for User({callback.user_id})")
        input_data: str = callback.payload[self.MARKER]

        event = self.announcement_service.find(input_data)
        vote_keyboard = markup.create_voter_inline_markup(self.MARKER, event.id)

        await callback.original.message.answer(msg.DELETE_ANNOUNCEMENT_VOTE, reply_markup=vote_keyboard)


class DeleteEventAfterVoteCallbackHandler(TelegramCallbackHandler, MenuGeneral):
    MARKER = DeleteAnnouncementBeforeVoteCallbackHandler.MARKER + markup.VOTE_MARK

    def __init__(self, announcement_service: AnnouncementService):
        TelegramCallbackHandler.__init__(self)
        MenuGeneral.__init__(self)
        self.announcement_service = announcement_service

    async def handle_(self, callback: CallbackMeta):
        logging.info(f"DeleteEventAfterVoteCallbackHandler.handle for User({callback.user_id})")
        vote_result: str = callback.payload[self.MARKER]

        if vote_result != EMPTY_VOTE_RESULT:
            announcement_id = vote_result
            self.announcement_service.delete(announcement_id)
            await callback.original.answer(msg.DELETE_ANNOUNCEMENT_DONE)
        else:
            await callback.original.answer(msg.DELETE_ANNOUNCEMENT_CANCELED)

        await self._show_menu(callback.original.message)
