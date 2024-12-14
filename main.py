import sys

import api
import db
import validation


def main():
    '''
    Основная функция скрипта.
    Во время запуска из командной строки считываются дата и
    список численных кодов валют.
    Необходимый формат даты: ДД.ММ.ГГГГ
    Необходимый формат кодов: дву- или трехзначные числа через
    запятую без пробелов.

    Логика работы:
        1. Проверяет наличие двух аргументов командной строки во время запуска.
        2. Проверяет правильность ввода даты.
        3. Проверяет правильность ввода кодов.
        4. Если были введены правильные коды, делает запрос к API
            и получает информацию о курсах соответствующих валют.
        5. Если все коды соответствуют валютам, записывает в БД данные,
            которые еще не были туда внесены.
        6. Считывает данные о курсах всех ранее запрошенных валют за
            введенную дату.
    '''

    try:
        validation.validate_input()
        date = validation.validate_date(sys.argv[1])
        codes = validation.validate_codes(sys.argv[2:])
        if codes:
            code_list = api.ApiGetAndParse(date).get_required_currencies(
                set(codes)
            )
            if code_list:
                with db.close_manager():
                    db.Inserter(date, code_list).insert_date()
                    db.Inserter(date, code_list).insert_rates()
        with db.close_manager():
            data = db.Reader().read(date)
            db.Reader().print(data)
    except Exception as e:
        print(e)


if __name__ == '__main__':
    main()
