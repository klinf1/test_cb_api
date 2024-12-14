from unittest.mock import patch

import pytest

import api
from exceptions import RequestError

date = '14.12.2024'


@pytest.fixture(scope='function')
def get_test_response():
    try:
        with open('tests/example_response.txt', 'r', encoding='utf-8') as f:
            example_text = f.read()
    except Exception:
        print('Ошибка! Файл с тестовым ответом сервера не найден.')
    else:
        return example_text


def test_get_rates_data_good_status_code():
    with patch('requests.post') as mock_post:
        mock_post.return_value.status_code = 200
        a = api.ApiGetAndParse(date).get_rates_data()
        err_msg = 'Проверьте, что при ответе сервера с кодом '
        err_msg += '200 get_rates_data возвращает response'
        assert a, err_msg


def test_get_rates_data_bad_status_code():
    with (patch('requests.post') as mock_post,
          pytest.raises(RequestError) as e_info):
        mock_post.return_value.status_code = 404
        api.ApiGetAndParse(date).get_rates_data()
        err_msg = 'Проверьте, что при ответе сервера с кодом, '
        err_msg += 'отличным от 200, вызывается RequestError'
        assert e_info.type is RequestError, err_msg


def test_parse_rates_data(get_test_response):
    with patch('requests.post') as mock_post:
        mock_post.return_value.status_code = 200
        mock_post.return_value.text = get_test_response
        a = api.ApiGetAndParse(date).parse_rates_data()
        err_msg = 'Проверьте, что при корректном ответе сервера parse_'
        err_msg += 'rates_data возвращает список словарей с курсами валют'
        assert a, err_msg
        assert type(a) is list, err_msg
        assert a[0].get('Vname') == 'Австралийский доллар', err_msg


def test_get_required_currencies(get_test_response):
    with patch('requests.post') as mock_post:
        mock_post.return_value.status_code = 200
        mock_post.return_value.text = get_test_response
        a = api.ApiGetAndParse(date).get_required_currencies(['36', '000'])
        err_msg = 'Проверьте, что get_required_currencies '
        err_msg += 'возвращает данные только для корректных кодов'
        assert a[0].get('Vcode') == '36', err_msg
        a = api.ApiGetAndParse(date).get_required_currencies(['000'])
        err_msg = 'Проверьте, что при отсутствии в запросе корректных кодов'
        err_msg += 'get_required_currencies возвращает False'
        assert a is False, err_msg
