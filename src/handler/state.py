from aiogram.dispatcher.filters.state import State, StatesGroup


class ShareHomeState(StatesGroup):
    waiting_for_city = State()
    waiting_for_info = State()


class ShareTripState(StatesGroup):
    waiting_for_city_from = State()
    waiting_for_city_to = State()
    waiting_for_scheduling = State()
    waiting_for_info = State()


class FindHomeState(StatesGroup):
    waiting_for_city = State()


class FindTripState(StatesGroup):
    waiting_for_city_from = State()
    waiting_for_city_to = State()
