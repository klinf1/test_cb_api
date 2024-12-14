import datetime
import requests
import xmltodict

from exceptions import RequestError
import logs


class ApiGetAndParse:
    '''
    Класс для получения и работы с данными о курсах валют, предоставленными
    API ЦБ РФ.
    Реализует метод GetCursOnDateXML.

    Переменные:
        date:str - строка с датой, за которую необходимо запросить курсы
        в формате ДД.ММ.ГГГГ.

    Методы:
        get_rates_data,
        parse_rates_data,
        get_required_currencies.
    '''

    def __init__(self, date: str) -> None:
        self.date = str(
            datetime.datetime.strptime(date, "%d.%m.%Y")
        ).replace(' ', 'T')

    __url = 'https://www.cbr.ru/DailyInfoWebServ/DailyInfo.asmx?WSDL'
    __headers = {
            'Host': 'www.cbr.ru',
            'Content-Type': 'application/soap+xml; charset=utf-8',
            'Content-Length': '1000',
    }
    __body = '''<?xml version="1.0" encoding="utf-8"?>
    <soap12:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap12="http://www.w3.org/2003/05/soap-envelope">
    <soap12:Body>
        <GetCursOnDateXML xmlns="http://web.cbr.ru/">
        <On_date>{}</On_date>
        </GetCursOnDateXML>
    </soap12:Body>
    </soap12:Envelope>'''

    def get_rates_data(self) -> requests.Response:
        '''
        Получает от API данные о курсах валют за заданную дату.

        Возвращает:
            requests.Response: объект Response
            с данными API, если код ответа сервера == 200.

        Исключения:
            RequestError, если соединение с сервером невозможно
            или код ответа сервера != 200.
        '''

        try:
            response = requests.post(
                url=self.__url,
                headers=self.__headers,
                data=self.__body.format(self.date)
            )
            logs.logger.info(
                f'Получен ответ от сервера c кодом {response.status_code}'
            )
        except requests.exceptions.RequestException:
            note = 'Невозможно установить соединение с сервером.'
            note += f' Код ответа: {response.status_code}'
            logs.logger.error(note)
            raise RequestError(response)
        else:
            if response.status_code != 200:
                logs.logger.error(
                    f'Отказ сервера. Код ответа: {response.status_code}'
                )
                raise RequestError(response)
            return response

    def parse_rates_data(self) -> list[dict]:
        '''
        Обрабатывает ответ сервера.

        Возвращает:
            Данные о курсах валют за заданную дату в формате
            списка словарей.
        '''

        text = xmltodict.parse(self.get_rates_data().text)
        rates_data = text.get(
            'soap:Envelope'
        ).get(
            'soap:Body'
        ).get(
            'GetCursOnDateXMLResponse'
        ).get(
            'GetCursOnDateXMLResult'
        ).get(
            'ValuteData'
        ).get(
            'ValuteCursOnDate'
        )
        logs.logger.info('Ответ сервера расшифрован')
        return rates_data

    def get_required_currencies(self, codes: list[str]) -> list[dict] | bool:
        '''
        Формирует список с данными запрошенных пользователем валют.

        Аргументы:
            codes: список, содержащий запрошенные коды в виде строк.

        Возвращает:
            Список словарей с данными о запрошенных валютах или False,
            если пользователь задал несуществующие коды валют.
        '''

        currency_list = [
            i for i in self.parse_rates_data() if i.get('Vcode') in codes
        ]
        found_codes = [item.get('Vcode') for item in currency_list]
        not_found_list = [code for code in codes if code not in found_codes]
        if not_found_list != []:
            logs.logger.warning(
                f'Данные коды не являются кодами валют: {not_found_list}'
            )
        if currency_list == []:
            logs.logger.warning('Заданы несуществующие коды валют.')
            return False
        return currency_list
