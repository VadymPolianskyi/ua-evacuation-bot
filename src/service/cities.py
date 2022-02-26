from src.config.msg import ANY_CITY_CHOICE

_all = [
    'Львів',
    'Київ',
    'Івано-Франківськ',
    'Тернопіль',
    'Вінниця',
    'Харків',
    'Рівне',
    'Луцьк',
    'Хмельницький',
    'Дніпро',
    'Чернівці',
    'Полтава',
    'Житомир',
    'Запоріжжя',
    'Черкаси',
    'Одеса',
    'Миколаїв',
    'Кропивницький',
    'Ужгород',
    'Чернігів',
    'Суми',
    'Херсон',
    'Донецьк',
    'Луганськ',
    'Сімферополь',
    'Кордон',
    'Закордон',
    'Кишинев',
    'Могилев-Подольск',
    'Паланика',
    'Молдова',
    'Румунія',
    'Польща'
]


def all(except_of: str = None, with_any=False) -> list:
    result = [c for c in _all if c != except_of]
    if with_any:
        result = any() + result
    return result


def any() -> list[str]:
    return ANY_CITY_CHOICE


def validate(city: str):
    print(f"Validating city '{city}'")
    return city in _all
