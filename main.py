import sys

import api
import db
import validation


def main():
    try:
        validation.validate_input()
        date = validation.validate_date(sys.argv[1])
        codes = validation.validate_codes(sys.argv[2:])
        if codes:
            code_list = api.ApiGetAndParse(date).get_required_currencies(
                set(codes)
            )
            if code_list:
                db.Inserter(date, code_list).insert_date()
                db.Inserter(date, code_list).insert_rates()
        data = db.Reader().read(date)
        db.Reader().print(data)
    except Exception as e:
        print(e)


if __name__ == '__main__':
    main()
