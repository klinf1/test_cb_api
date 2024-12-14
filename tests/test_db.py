import os
from unittest import mock

import pytest

import db


test_date = '12.12.2024'
test_items = [{'Vname': 'Австралийский доллар',
               'Vnom': '1',
               'Vcurs': '65.8247',
               'Vcode': '36',
               'VchCode': 'AUD',
               'VunitRate':
               '65.8247'}]


@pytest.fixture(scope='function')
def get_test_inserter():
    with mock.patch.object(db.BaseDb, '__db_name', 'test.db'):
        a = db.Inserter(test_date, test_items)
    yield a
    if os.path.exists('test.db'):
        a.close()
        os.remove('test.db')


@pytest.fixture(scope='function')
def get_test_reader():
    with mock.patch.object(db.BaseDb, '__db_name', 'test.db'):
        a = db.Reader()
    yield a
    if os.path.exists('test.db'):
        a.close()
        os.remove('test.db')


def test_insert_new_date(get_test_inserter):
    err_msg = 'Проверьте, что insert_date заносит данные в базу'
    assert get_test_inserter.insert_date(), err_msg
    err_msg = 'Проверьте, что insert_date не заносит дубликаты дат в базу'
    assert not get_test_inserter.insert_date(), err_msg


def test_insert_rates(get_test_inserter):
    err_msg = 'Проверьте, что insert_rates вносит данные в базу'
    assert get_test_inserter.insert_rates(), err_msg


def test_check_existing_rates(get_test_inserter):
    get_test_inserter.insert_date()
    get_test_inserter.insert_rates()
    new_items = get_test_inserter.check_existing_rates()
    err_msg = 'Проверьте, что check_existing_rates '
    err_msg += 'удаляет из запроса данные, уже присутствующие в БД'
    assert new_items == [], err_msg


def test_read(get_test_inserter, get_test_reader):
    get_test_inserter.insert_date()
    get_test_inserter.insert_rates()
    get_test_inserter.close()
    reader = get_test_reader.read(test_date)
    result = reader.fetchone()
    expected = (1, '12.12.2024', 'Австралийский доллар', 1, '65.8247')
    err_msg = 'Проверьте, что read корректно считывает данные из БД'
    assert result == expected, err_msg
