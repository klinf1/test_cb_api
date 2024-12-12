import datetime
import re
import sys


def validate_input() -> bool:
    try:
        sys.argv[1]
        sys.argv[2]
    except Exception:
        return False
    return True


def validate_date(input: str) -> str | bool:
    try:
        current_date = datetime.datetime.now()
        input_date = datetime.datetime.strptime(input, '%d.%m.%Y')
    except Exception:
        return False
    if input_date > current_date:
        return False
    return input_date.strftime('%d.%m.%Y')


def validate_codes(input: list[str]) -> list[list[str]]:
    if len(input) > 1:
        return False
    code_list = input[0].split(',')
    digits = re.compile('\D+')
    bad_codes = [
        code for code in code_list if digits.findall(code) != [] or len(code)
        not in (2, 3)
    ]
    good_codes = [code for code in code_list if code not in bad_codes]
    return [good_codes, bad_codes]
