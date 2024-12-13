import datetime
import requests
import xmltodict

from exceptions import RequestError


class ApiGetAndParse:
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

    def get_rates_data(self) -> dict:
        try:
            response = requests.post(
                url=self.__url,
                headers=self.__headers,
                data=self.__body.format(self.date)
            )
        except requests.exceptions.RequestException:
            raise RequestError(response)
        return response.text

    def parse_rates_data(self) -> list[dict]:
        text = xmltodict.parse(self.get_rates_data())
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
        return rates_data

    def get_required_currencies(self, codes: list[str]) -> list[dict] | bool:
        currency_list = [
            i for i in self.parse_rates_data() if i.get('Vcode') in codes
        ]
        found_codes = [item.get('Vcode') for item in currency_list]
        not_found_list = [code for code in codes if code not in found_codes]
        if not_found_list != []:
            print(f'Данные коды не являются кодами валют: {not_found_list}')
        if currency_list == []:
            return False
        return currency_list
