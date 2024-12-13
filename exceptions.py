import requests
import sqlite3


class InputError(Exception):
    def __str__(self):
        note = 'Не введены дата и/или список кодов.'
        note += '\nПовторите запуск, указав дату в формате ДД.ММ.ГГГГ'
        note += ' и числовые коды валют (двух- или трехзначные числа)'
        note += ' через запятую без пробелов'
        return note


class DateInputError(Exception):
    def __str__(self):
        note = 'Дата введена неверно.'
        note += '\nПовторите запуск, указав дату в формате ДД.ММ.ГГГГ'
        return note


class DateOutOfRangeError(Exception):
    def __str__(self):
        note = 'Введенная дата больше текущей.'
        note += '\nПовторите запуск, указав верную дату в формате ДД.ММ.ГГГГ'
        return note


class AdditionalArgumentsError(Exception):
    def __str__(self):
        note = 'Список кодов содержит пробелы.'
        note += '\nПовторите запуск, указывая коды через запятую без пробелов'
        return note


class RequestError(Exception):
    def __init__(self, response: requests.Response):
        self.response = response

    def __str__(self):
        note = f'Отказ сервера. Код ответа: {self.response.status_code}'
        return note


class DbCreationError(sqlite3.OperationalError):
    def __str__(self):
        note = 'Ошибка создания таблиц в БД.'
        return note


class DbDateError(sqlite3.OperationalError):
    def __str__(self):
        note = 'Ошибка внесения даты в БД.'
        return note


class DbCheckError(sqlite3.OperationalError):
    def __str__(self):
        note = 'Ошибка проверки данных в БД.'
        return note


class DbRatesError(sqlite3.OperationalError):
    def __str__(self):
        note = 'Ошибка внесения курсов в БД.'
        return note


class DbReadError(sqlite3.OperationalError):
    def __str__(self):
        note = 'Ошибка чтения данных из БД.'
        return note
