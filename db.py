import sqlite3
from contextlib import contextmanager

import prettytable

from exceptions import (DbCheckError,
                        DbCreationError,
                        DbDateError,
                        DbRatesError,
                        DbReadError)
import logs


class BaseDb:
    db_name = 'data.db'

    def __init__(self):
        self._con = sqlite3.connect(self.db_name)
        self._cur = self._con.cursor()
        try:
            query_orders = '''SELECT count(*) FROM sqlite_master
                              WHERE type='table' AND name='currency_orders';'''
            query_rates = '''SELECT count(*) FROM sqlite_master
                             WHERE type='table' AND name='currency_rates';'''
            with self._con:
                (orders_exists,) = self._cur.execute(query_orders).fetchone()
                (rates_exists,) = self._cur.execute(query_rates).fetchone()
                if orders_exists == 0:
                    query = ('''CREATE TABLE currency_orders
                                (id INTEGER PRIMARY KEY,
                                ondate TEXT)
                        ''')
                    self._cur.execute(query)
                    logs.logger.info('Создана таблица currency_orders')
                if rates_exists == 0:
                    query = ('''CREATE TABLE if NOT EXISTS currency_rates
                                (order_id INTEGER,
                                name TEXT NOT NULL,
                                numeric_code TEXT NOT NULL,
                                alphabetic_code TEXT NOT NULL,
                                scale INT NOT NULL,
                                rate TEXT NOT NULL,
                                FOREIGN KEY (order_id)
                                REFERENCES currency_order (id)
                                    ON DELETE CASCADE)
                    ''')
                    self._cur.execute(query)
                    logs.logger.info('Создана таблица currency_rates')
        except sqlite3.OperationalError as e:
            logs.logger.error(f'Ошибка БД: создание таблиц {e}')
            raise DbCreationError

    def close(self):
        self._con.close()


class Inserter(BaseDb):
    def __init__(self, date: str, items: list[dict]):
        super().__init__()
        self.date = date
        self.items = items

    def insert_date(self) -> None:
        try:
            query = '''SELECT COUNT(*) FROM currency_orders WHERE ondate=?'''
            self._cur.execute(query, (self.date,))
            (exists,) = self._cur.fetchone()
            if exists == 0:
                query = '''INSERT INTO currency_orders (ondate) VALUES (?)'''
                self._cur.execute(query, (self.date,))
                self._con.commit()
                done = True
                logs.logger.info(f'Дата {self.date} внесена в БД')
            else:
                done = False
                logs.logger.info(f'Дата {self.date} уже присутствует в БД')
        except sqlite3.OperationalError as e:
            logs.logger.error(f'Ошибка БД: внесение даты - {e}')
            raise DbDateError
        else:
            return done

    def check_existing_rates(self) -> list[dict]:
        try:
            query = '''SELECT currency_rates.numeric_code
                       FROM currency_rates
                       JOIN currency_orders
                       WHERE currency_orders.id=currency_rates.order_id
                       AND currency_orders.ondate=?'''
            self._cur.execute(query, (self.date,))
            existing_rates = [rate for (rate,) in self._cur.fetchall()]
            new_rates = [
                i for i in self.items if i.get('Vcode') not in existing_rates
            ]
            if existing_rates != []:
                logs.logger.info(
                    f'Курсы валют с кодами {existing_rates} уже находятся в БД'
                )
            if new_rates == []:
                logs.logger.info('Не найдено новых данных для внесения')
            return new_rates
        except sqlite3.OperationalError as e:
            logs.logger.error(
                f'Ошибка БД: проверка на наличие уже внесенных данных - {e}'
            )
            raise DbCheckError

    def insert_rates(self) -> None:
        try:
            to_insert = self.check_existing_rates()
            query = '''
                INSERT INTO currency_rates (
                    order_id,
                    name,
                    numeric_code,
                    alphabetic_code,
                    scale,
                    rate
                ) VALUES (
                    (SELECT id FROM currency_orders WHERE ondate=?),
                    ?,?,?,?,?)
                '''
            done = False
            if to_insert != []:
                for item in to_insert:
                    self._cur.execute(query, (
                        (self.date),
                        item.get('Vname'),
                        item.get('Vcode'),
                        item.get('VchCode'),
                        int(item.get('Vnom')),
                        item.get('Vcurs')
                    ))
                self._con.commit()
                done = True
                logs.logger.info('Данные о запрошенных курсах внесены в БД')
        except sqlite3.OperationalError as e:
            logs.logger.error(f'Ошибка БД: внесение курсов - {e}')
            raise DbRatesError
        else:
            return done


class Reader(BaseDb):
    def __init__(self):
        super().__init__()

    def read(self, date: str) -> None:
        try:
            query = '''SELECT
                        currency_rates.order_id,
                        currency_orders.ondate,
                        currency_rates.name,
                        currency_rates.scale,
                        currency_rates.rate
                       FROM currency_rates
                           INNER JOIN currency_orders
                               ON currency_rates.order_id=currency_orders.id
                                WHERE currency_orders.ondate=?
                       ORDER BY currency_rates.name ASC'''
            data = self._cur.execute(query, (date,))
            logs.logger.info(f'Данные за {date} загружены из БД')
            return data
        except sqlite3.OperationalError as e:
            logs.logger.error(f'Ошибка БД: чтение данных - {e}')
            raise DbReadError

    def print(self, to_print: sqlite3.Cursor):
        table = prettytable.PrettyTable()
        table = prettytable.from_db_cursor(to_print)
        table.field_names = ['Номер распоряжения',
                             'Дата установки курса',
                             'Валюта',
                             'Номинал',
                             'Курс']
        print(table)


@contextmanager
def close_manager():
    yield
    BaseDb().close()
