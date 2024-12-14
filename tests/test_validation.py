import sys
import datetime
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
        assert v_input is True
    with mock.patch.object(
        sys, 'argv', bad_argv_date
    ), pytest.raises(exceptions.InputError):
        v_input = validation.validate_input()
    with mock.patch.object(
        sys, 'argv', bad_argv_codes
    ), pytest.raises(exceptions.InputError):
        v_input = validation.validate_input()
    with mock.patch.object(
        sys, 'argv', empty_argv
    ), pytest.raises(exceptions.InputError):
        v_input = validation.validate_input()


def test_validate_date():
    good_date = '12.12.2024'
    timedelta = datetime.timedelta(days=1)
    late_date = (datetime.datetime.now() + timedelta).strftime('%d.%m.%Y')
    bad_date = 'bad_date'
    with pytest.raises(exceptions.DateInputError):
        v_date = validation.validate_date(bad_date)
    with pytest.raises(exceptions.DateOutOfRangeError):
        v_date = validation.validate_date(late_date)
    v_date = validation.validate_date(good_date)
    assert v_date == good_date


def test_validate_codes():
    good_codes = ['123,36,24']
    spaces_codes = ['123', '36,24']
    some_wrong_codes = ['213,gew,, 2,03,23455,wq1']
    some_letter_codes = ['123,een,36,1qwe']
    all_letter_codes = ['qwe,egjgf']
    long_codes = ['1234,12345']
    short_codes = ['0,1,2']
    with pytest.raises(exceptions.AdditionalArgumentsError):
        validation.validate_codes(spaces_codes)
    v_codes = validation.validate_codes(short_codes)
    assert v_codes is False
    v_codes = validation.validate_codes(long_codes)
    assert v_codes is False
    v_codes = validation.validate_codes(all_letter_codes)
    assert v_codes is False
    v_codes = validation.validate_codes(some_letter_codes)
    assert v_codes == ['123', '36']
    v_codes = validation.validate_codes(some_wrong_codes)
    assert v_codes == ['213', '03']
    v_codes = validation.validate_codes(good_codes)
    assert v_codes == ['123', '36', '24']
