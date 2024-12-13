import datetime
import re
import sys

from exceptions import (AdditionalArgumentsError,
                        DateInputError,
                        DateOutOfRangeError,
                        InputError,)
import logs


def validate_input() -> bool:
    try:
        sys.argv[1]
        sys.argv[2]
    except Exception:
        logs.logger.error('Дата и/или список кодов не введены')
        raise InputError
    return True


def validate_date(input: str) -> str:
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
