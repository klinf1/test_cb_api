import datetime
import re
import sys

from exceptions import (AdditionalArgumentsError,
                        DateInputError,
                        DateOutOfRangeError,
                        InputError,)
import logs


def validate_input() -> bool:
    '''
    Проверяет факт ввода даты и кодов.
    Логирует факт неправильного ввода.

    Возвращает:
        True, если аргументы введены.

    Исключения:
        InputError: вызывается, если не введены дата
        и/или коды.
    '''

    try:
        sys.argv[1]
        sys.argv[2]
    except Exception:
        logs.logger.error('Дата и/или список кодов не введены')
        raise InputError
    return True


def validate_date(input: str) -> str:
    '''
    Проверяет правильность ввода даты.
    Логирует факт неправильного ввода.

    Возвращает:
        введенную дату, если ее формат верен.

    Исключения:
        DateInputError: вызывается, если формат даты не
            соответствует ДД.ММ.ГГГГ.
        DateOutOfRangeError: вызывается, если введенная
            дата больше текущей.
    '''

    try:
        current_date = datetime.datetime.now()
        input_date = datetime.datetime.strptime(input, '%d.%m.%Y')
    except Exception:
        logs.logger.error(f'Дата введена неверно: {input}')
        raise DateInputError
    if input_date > current_date:
        logs.logger.error(f'Введенная дата больше текущей: {input_date}')
        raise DateOutOfRangeError
    return input_date.strftime('%d.%m.%Y')


def validate_codes(input: list[str]) -> list[str] | bool:
    '''
    Проверяет правильность ввода кодов валют.
    Логирует неправильно введенные коды.

    Необходимый формат ввода кодов: дву- или трехзначные числа,
    введенные через запятую без пробелов.

    Возвращает:
        Список кодов, соответствующих формату или False, если таких
        в запросе нет.

    Исключения:
        AdditionalArgumentsError: вызывается, если в списке кодов есть пробелы.
    '''

    if len(input) > 1:
        logs.logger.error(f'В списке кодов присутствуют пробелы: {input}')
        raise AdditionalArgumentsError
    code_list = input[0].split(',')
    digits = re.compile('\D+')
    bad_codes = [
        code for code in code_list if digits.findall(code) != [] or len(code)
        not in (2, 3)
    ]
    good_codes = [code for code in code_list if code not in bad_codes]
    if bad_codes != []:
        note = 'Коды валют должны быть дву- или трехзначными числами.'
        note += f' Данные коды не являются кодами валют: {bad_codes}'
        logs.logger.warning(note)
    if good_codes == []:
        logs.logger.warning('В запросе не найдено кодов необходимого формата.')
        return False
    return good_codes
