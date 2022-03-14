import asyncio
import logging

from aiogram import Bot, Dispatcher, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import Message

from src.config import config
from src.handler.find.black_list import BlackListCallbackHandler
from src.handler.find.find import FindCallbackHandler
from src.handler.find.find_create import FindCreateCallbackHandler
from src.handler.find.find_help import FindHelpCallbackHandler, FindHelpCityAnswerHandler
from src.handler.find.find_home import FindHomeCallbackHandler, FindHomeCityAnswerHandler
from src.handler.find.find_my import FindMyAnnouncementsCallbackHandler
from src.handler.find.find_trip import FindTripCallbackHandler, FindTripCityFromAnswerHandler, \
    FindTripCityToAnswerHandler
from src.handler.info import InfoCallbackHandler
from src.handler.menu import MenuHandler, MenuCallbackHandler
from src.handler.my import MyAnnouncementsCallbackHandler, DeleteAnnouncementBeforeVoteCallbackHandler, \
    DeleteEventAfterVoteCallbackHandler
from src.handler.router import CallbackRouter
from src.handler.share.share import ShareCallbackHandler
from src.handler.share.share_help import ShareHelpCallbackHandler, ShareHelpPostCityAnswerHandler, \
    ShareHelpPostInfoAnswerHandler
from src.handler.share.share_home import ShareHomeCallbackHandler, ShareHomePostInfoAnswerHandler
from src.handler.share.share_home import ShareHomePostCityAnswerHandler
from src.handler.share.share_trip import ShareTripCallbackHandler, ShareTripCityToAnswerHandler, \
    ShareTripCityFromAnswerHandler, ShareTripSchedulingAnswerHandler, ShareTripInfoAnswerHandler, \
    ShareTripSchedulingAnswerCallbackHandler
from src.handler.state import ShareHomeState, ShareTripState, FindHomeState, FindTripState, ShareHelpState, \
    FindHelpState
from src.service.announcement import AnnouncementService
from src.service.city import CityService
from src.service.scheduler import Scheduler
from src.service.user import UserService

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.getLevelName(config.LOG_LEVEL))

#### TG BOT ####
bot = Bot(token=config.BOT_API_TOKEN, parse_mode=config.PARSE_MODE)
dp = Dispatcher(bot, storage=MemoryStorage())

#### SERVICES ####
announcement_service = AnnouncementService()
city_service = CityService()
user_service = UserService()
sch = Scheduler()

#### CALLBACK ####
callback_router = CallbackRouter([
    MenuCallbackHandler(user_service, announcement_service),
    ShareCallbackHandler(announcement_service, city_service),
    FindCallbackHandler(announcement_service),
    MyAnnouncementsCallbackHandler(announcement_service),
    InfoCallbackHandler(),

    ShareHomeCallbackHandler(city_service),
    ShareTripCallbackHandler(city_service),
    ShareTripSchedulingAnswerCallbackHandler(),
    ShareHelpCallbackHandler(city_service),

    FindHomeCallbackHandler(city_service),
    FindTripCallbackHandler(city_service),
    FindHelpCallbackHandler(city_service),
    BlackListCallbackHandler(user_service),

    FindCreateCallbackHandler(announcement_service),
    FindMyAnnouncementsCallbackHandler(announcement_service),

    DeleteAnnouncementBeforeVoteCallbackHandler(announcement_service),
    DeleteEventAfterVoteCallbackHandler(announcement_service, user_service)
])

#### HANDLERS ####
menu_handler = MenuHandler(user_service, announcement_service)

find_home_city_answer_handler = FindHomeCityAnswerHandler(announcement_service, city_service)

share_home_post_city_answer_handler = ShareHomePostCityAnswerHandler(city_service)
share_home_post_info_answer_handler = ShareHomePostInfoAnswerHandler(announcement_service, city_service)

share_trip_city_from_answer_handler = ShareTripCityFromAnswerHandler(city_service)
share_trip_city_to_answer_handler = ShareTripCityToAnswerHandler(city_service)
share_trip_scheduling_answer_handler = ShareTripSchedulingAnswerHandler(city_service)
share_trip_info_answer_handler = ShareTripInfoAnswerHandler(announcement_service, city_service)

find_trip_city_from_answer_handler = FindTripCityFromAnswerHandler(city_service)
find_trip_city_to_answer_handler = FindTripCityToAnswerHandler(announcement_service, city_service)

share_help_post_city_answer_handler = ShareHelpPostCityAnswerHandler(city_service)
share_help_post_info_answer_handler = ShareHelpPostInfoAnswerHandler(announcement_service, city_service)

find_help_city_answer_handler = FindHelpCityAnswerHandler(announcement_service, city_service)


#################################
#       HANDLER ROUTING         #
#################################

@dp.message_handler(commands=['start', 'help', 'menu'])
async def menu(message: Message):
    if not user_service.find_or_create(message.from_user.id):
        user_service.save(message.from_user.id)

    await menu_handler.handle(message)


# share home

@dp.message_handler(state=ShareHomeState.waiting_for_city)
async def share_home_city_answer(message):
    await share_home_post_city_answer_handler.handle(message)


@dp.message_handler(state=ShareHomeState.waiting_for_info)
async def share_home_info_answer(message):
    await share_home_post_info_answer_handler.handle(message)


# share trip

@dp.message_handler(state=ShareTripState.waiting_for_city_from)
async def share_trip_city_from_answer(message):
    await share_trip_city_from_answer_handler.handle(message)


@dp.message_handler(state=ShareTripState.waiting_for_city_to)
async def share_trip_city_to_answer(message):
    await share_trip_city_to_answer_handler.handle(message)


@dp.message_handler(state=ShareTripState.waiting_for_scheduling)
async def share_trip_scheduling_answer(message):
    await share_trip_scheduling_answer_handler.handle(message)


@dp.message_handler(state=ShareTripState.waiting_for_info)
async def share_trip_info_answer(message):
    await share_trip_info_answer_handler.handle(message)


# share help

@dp.message_handler(state=ShareHelpState.waiting_for_city)
async def share_help_city_answer(message):
    await share_help_post_city_answer_handler.handle(message)


@dp.message_handler(state=ShareHelpState.waiting_for_info)
async def share_help_info_answer(message):
    await share_help_post_info_answer_handler.handle(message)


# find home

@dp.message_handler(state=FindHomeState.waiting_for_city)
async def find_home_city_answer(message):
    await find_home_city_answer_handler.handle(message)


# find help

@dp.message_handler(state=FindHelpState.waiting_for_city)
async def find_help_city_answer(message):
    await find_help_city_answer_handler.handle(message)


# find trip

@dp.message_handler(state=FindTripState.waiting_for_city_from)
async def find_trip_city_from_answer(message):
    await find_trip_city_from_answer_handler.handle(message)


@dp.message_handler(state=FindTripState.waiting_for_city_to)
async def find_trip_city_to_answer(message):
    await find_trip_city_to_answer_handler.handle(message)


#################################
#       GENERAL CALLBACK        #
#################################

@dp.callback_query_handler(state="*")
async def callback_handler(call):
    await callback_router.route(call)


##############################
#       APP LAUNCHING        #
##############################


async def on_startup(_):
    await bot.set_webhook(config.WEBHOOK_URL + config.BOT_API_TOKEN)


async def on_shutdown(dp):
    logging.info('Shutting down..')

    await bot.delete_webhook()

    await dp.storage.close()
    await dp.storage.wait_closed()
    announcement_service.close()

    logging.info('Bye!')


if __name__ == "__main__":
    logging.info("Lanuch")
    sch.run()

    executor.start_webhook(
        dispatcher=dp,
        webhook_path='/' + config.BOT_API_TOKEN,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
        skip_updates=True,
        host=config.SERVER_HOST,
        port=config.SERVER_PORT,
    )
    # asyncio.run(executor.start_polling(dispatcher=dp))
