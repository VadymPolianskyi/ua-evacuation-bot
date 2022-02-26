from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from src.config import msg

VOTE_MARK = '_v'
EMPTY_VOTE_RESULT = '_'


def create_voter_inline_markup(vote_prefix: str, value: str):
    return create_inline_markup(vote_prefix + VOTE_MARK, [(msg.YES, value), (msg.NO, EMPTY_VOTE_RESULT)])


def create_simple_inline_markup(key, button_names: list):
    buttons = [(e, e) for e in button_names]
    return create_inline_markup(key, buttons)


def create_inline_markup(key, button_name_value_tuples: list):
    button_name_key_value_tuples = [(e[0], key, e[1]) for e in button_name_value_tuples]

    return create_inline_markup_(button_name_key_value_tuples)


def create_inline_markup_(button_name_key_value_tuples: list, buttons_in_line=2):
    keyboard = list()
    line = list()
    for element in button_name_key_value_tuples:
        b_name, b_key, b_value = element

        if len(line) >= buttons_in_line:
            keyboard.append(line.copy())
            line.clear()

        line.append(InlineKeyboardButton(text=b_name, callback_data='{"' + b_key + '": "' + b_value + '"}'))

    keyboard.append(line)
    return InlineKeyboardMarkup(inline_keyboard=keyboard, resize_keyboard=False)
