import datetime
import re
import sys

from exceptions import (AdditionalArgumentsError,
                        DateInputError,
                        DateOutOfRangeError,
                        InputError,)


def validate_input() -> bool:
    try:
        sys.argv[1]
        sys.argv[2]
    except Exception:
        raise InputError
    return True


def validate_date(input: str) -> str:
    try:
        current_date = datetime.datetime.now()
        input_date = datetime.datetime.strptime(input, '%d.%m.%Y')
    except Exception:
        raise DateInputError
    if input_date > current_date:
        raise DateOutOfRangeError
    return input_date.strftime('%d.%m.%Y')


def validate_codes(input: list[str]) -> list[str] | bool:
    if len(input) > 1:
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
        note += f'\nДанные коды не являются кодами валют: {bad_codes}'
        print(note)
    if good_codes == []:
        return False
    return good_codes
