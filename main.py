import asyncio

from aiogram import Bot, Dispatcher, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from src.config import config
from src.handler.find.find import FindCallbackHandler
from src.handler.find.find_home import FindHomeCallbackHandler, FindHomeCityAnswerHandler
from src.handler.find.find_trip import FindTripCallbackHandler, FindTripCityFromAnswerHandler, \
    FindTripCityToAnswerHandler
from src.handler.info import InfoCallbackHandler
from src.handler.menu import MenuHandler, MenuCallbackHandler
from src.handler.my import MyAnnouncementsCallbackHandler, DeleteAnnouncementBeforeVoteCallbackHandler, \
    DeleteEventAfterVoteCallbackHandler
from src.handler.router import CallbackRouter
from src.handler.share.share import ShareCallbackHandler
from src.handler.share.share_home import ShareHomeCallbackHandler, ShareHomePostInfoAnswerHandler
from src.handler.share.share_home import ShareHomePostCityAnswerHandler
from src.handler.share.share_trip import ShareTripCallbackHandler, ShareTripCityToAnswerHandler, \
    ShareTripCityFromAnswerHandler, ShareTripSchedulingAnswerHandler, ShareTripInfoAnswerHandler
from src.handler.state import ShareHomeState, ShareTripState, FindHomeState, FindTripState
from src.service.announcement import AnnouncementService

#### TG BOT ####
bot = Bot(token=config.BOT_API_TOKEN, parse_mode=config.PARSE_MODE)
dp = Dispatcher(bot, storage=MemoryStorage())

#### SERVICES ####
announcement_service = AnnouncementService()

#### CALLBACK ####
callback_router = CallbackRouter([
    MenuCallbackHandler(),
    ShareCallbackHandler(),
    FindCallbackHandler(),
    MyAnnouncementsCallbackHandler(announcement_service),
    InfoCallbackHandler(),

    ShareHomeCallbackHandler(),
    ShareTripCallbackHandler(),

    FindHomeCallbackHandler(),
    FindTripCallbackHandler(),

    DeleteAnnouncementBeforeVoteCallbackHandler(announcement_service),
    DeleteEventAfterVoteCallbackHandler(announcement_service)
])

#### HANDLERS ####
menu_handler = MenuHandler()

find_home_city_answer_handler = FindHomeCityAnswerHandler(announcement_service)

share_home_post_city_answer_handler = ShareHomePostCityAnswerHandler()
share_home_post_info_answer_handler = ShareHomePostInfoAnswerHandler(announcement_service)

share_trip_city_from_answer_handler = ShareTripCityFromAnswerHandler()
share_trip_city_to_answer_handler = ShareTripCityToAnswerHandler()
share_trip_scheduling_answer_handler = ShareTripSchedulingAnswerHandler()
share_trip_info_answer_handler = ShareTripInfoAnswerHandler(announcement_service)

find_trip_city_from_answer_handler = FindTripCityFromAnswerHandler()
find_trip_city_to_answer_handler = FindTripCityToAnswerHandler(announcement_service)


#################################
#       HANDLER ROUTING         #
#################################

@dp.message_handler(commands=['start', 'help', 'menu'])
async def menu(message):
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


# find home

@dp.message_handler(state=FindHomeState.waiting_for_city)
async def find_home_city_answer(message):
    await find_home_city_answer_handler.handle(message)


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
    print('Shutting down..')

    await bot.delete_webhook()

    await dp.storage.close()
    await dp.storage.wait_closed()

    print('Bye!')


if __name__ == "__main__":
    # executor.start_webhook(
    #     dispatcher=dp,
    #     webhook_path='/' + config.BOT_API_KEY,
    #     on_startup=on_startup,
    #     on_shutdown=on_shutdown,
    #     skip_updates=True,
    #     host=config.SERVER_HOST,
    #     port=config.SERVER_PORT,
    # )
    print("Lanuch")
    asyncio.run(executor.start_polling(dispatcher=dp))
