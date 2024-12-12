import sqlite3

import prettytable


class BaseDb():

    def __init__(self):
        self._con = sqlite3.connect('data.db')
        query = ('''CREATE TABLE if NOT EXISTS currency_orders
                    (id INTEGER PRIMARY KEY,
                    ondate TEXT)
        ''')
        with self._con:
            self._con.execute(query)
        query = ('''CREATE TABLE if NOT EXISTS currency_rates
                    (order_id INTEGER,
                    name TEXT NOT NULL,
                    numeric_code TEXT NOT NULL,
                    alphabetic_code TEXT NOT NULL,
                    scale INT NOT NULL,
                    rate TEXT NOT NULL,
                    FOREIGN KEY (order_id)
                        REFERENCES currency_order (id) ON DELETE CASCADE)
        ''')
        with self._con:
            self._con.execute(query)
        self._cur = self._con.cursor()

    def close(self):
        self._con.close()


class Inserter(BaseDb):
    def __init__(self, date: str, items: list[dict]):
        super().__init__()
        self.date = date
        self.items = items

    def insert_date(self):
        query = '''SELECT COUNT(*) FROM currency_orders WHERE ondate=?'''
        self._cur.execute(query, (self.date,))
        (exists,) = self._cur.fetchone()
        if exists == 0:
            query = '''INSERT INTO currency_orders (ondate) VALUES (?)'''
            self._cur.execute(query, (self.date,))
            self._con.commit()
        else:
            print('date exists')
        self.close()

    def check_existing_rates(self) -> list[dict]:
        query = '''SELECT currency_rates.numeric_code
                   FROM currency_rates
                   JOIN currency_orders
                   WHERE currency_orders.id=currency_rates.order_id
                   AND currency_orders.ondate=?'''
        self._cur.execute(query, (self.date,))
        existing_rates = [rate for (rate,) in self._cur.fetchall()]
        new_rates = []
        for item in self.items:
            if item.get('Vcode') not in existing_rates:
                new_rates.append(item)
        return new_rates

    def insert_rates(self):
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
        self.close()


class Reader(BaseDb):
    def __init__(self, date: str):
        super().__init__()
        self.date = date

    def read(self):
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
        self._cur.execute(query, (self.date,))
        table = prettytable.PrettyTable()
        table = prettytable.from_db_cursor(self._cur)
        table.field_names = ['Номер распоряжения',
                             'Дата установки курса',
                             'Валюта',
                             'Номинал',
                             'Курс']
        print(table)
        self.close()
