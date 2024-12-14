import datetime
import sys
from unittest import mock

import pytest

import exceptions
import validation


def test_validate_input():
    good_argv = ['func_name', '12.12.2024', '36']
    bad_argv_date = ['func_name', '12.12.2024']
    bad_argv_codes = ['func_name', '36']
    empty_argv = []
    with mock.patch.object(sys, 'argv', good_argv):
        v_input = validation.validate_input()
        err_msg = 'Проверьте, что validate_input работает корректно'
        assert v_input is True, err_msg
    with mock.patch.object(
        sys, 'argv', bad_argv_date
    ), pytest.raises(exceptions.InputError) as e_info:
        v_input = validation.validate_input()
        err_msg = 'Проверьте, что запуск скрипта без кодов валют '
        err_msg += 'приводит к InputError'
        assert e_info.type is exceptions.InputError, err_msg
    with mock.patch.object(
        sys, 'argv', bad_argv_codes
    ), pytest.raises(exceptions.InputError) as e_info:
        v_input = validation.validate_input()
        err_msg = 'Проверьте, что запуск скрипта без даты '
        err_msg += 'приводит к InputError'
        assert e_info.type is exceptions.InputError, err_msg
    with mock.patch.object(
        sys, 'argv', empty_argv
    ), pytest.raises(exceptions.InputError) as e_info:
        v_input = validation.validate_input()
        err_msg = 'Проверьте, что запуск скрипта данных '
        err_msg += 'приводит к InputError'
        assert e_info.type is exceptions.InputError, err_msg


def test_validate_date():
    good_date = '12.12.2024'
    timedelta = datetime.timedelta(days=1)
    late_date = (datetime.datetime.now() + timedelta).strftime('%d.%m.%Y')
    bad_date = 'bad_date'
    with pytest.raises(exceptions.DateInputError) as e_info:
        v_date = validation.validate_date(bad_date)
        err_msg = 'Проверьте, что запуск скрипта с датой в неверном формате'
        err_msg += ' приводит к DateInputError'
        assert e_info.type is exceptions.DateInputError
    with pytest.raises(exceptions.DateOutOfRangeError) as e_info:
        v_date = validation.validate_date(late_date)
        err_msg = 'Проверьте, что запуск скрипта с еще не наступившей датой'
        err_msg += ' приводит к DateOutOfRangeError'
        assert e_info.type is exceptions.DateOutOfRangeError
    v_date = validation.validate_date(good_date)
    err_msg = 'Проверьте, что корректно введенная дата не вызывает исключений'
    assert v_date == good_date, err_msg


def test_validate_codes():
    good_codes = ['123,36,24']
    spaces_codes = ['123', '36,24']
    some_wrong_codes = ['213,gew,, 2,03,23455,wq1']
    some_letter_codes = ['123,een,36,1qwe']
    all_letter_codes = ['qwe,egjgf']
    long_codes = ['1234,12345']
    short_codes = ['0,1,2']
    with pytest.raises(exceptions.AdditionalArgumentsError) as e_info:
        validation.validate_codes(spaces_codes)
        err_msg = 'Проверьте, что наличие пробелов в списке кодов вызывает'
        err_msg += 'AdditionalArgumentsError'
        assert e_info.type is exceptions.AdditionalArgumentsError, e_info
    v_codes = validation.validate_codes(short_codes)
    err_msg = 'Проверьте, что отбрасываются слишком короткие коды'
    assert v_codes is False, err_msg
    v_codes = validation.validate_codes(long_codes)
    err_msg = 'Проверьте, что отбрасываются слишком длинные коды'
    assert v_codes is False, err_msg
    v_codes = validation.validate_codes(all_letter_codes)
    err_msg = 'Проверьте, что отбрасываются коды, состоящие не из цифр'
    assert v_codes is False, err_msg
    v_codes = validation.validate_codes(some_letter_codes)
    err_msg = 'Проверьте, что из всех кодов выбираются корректные'
    assert v_codes == ['123', '36'], err_msg
    v_codes = validation.validate_codes(some_wrong_codes)
    err_msg = 'Проверьте, что из всех кодов выбираются корректные'
    assert v_codes == ['213', '03'], err_msg
    v_codes = validation.validate_codes(good_codes)
    err_msg = 'Проверьте, что выбираются все корректные коды'
    assert v_codes == ['123', '36', '24'], err_msg
