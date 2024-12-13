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
            code_list = api.ApiGetAndParse(date).get_required_currencies(codes)
            db.Inserter(date, code_list).insert_date()
            db.Inserter(date, code_list).insert_rates()
        db.Reader(date).read()
    except Exception as e:
        print(e)


if __name__ == '__main__':
    main()