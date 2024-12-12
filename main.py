import sys

import api
import db
import validation


def main():
    try:
        if not validation.validate_input():
            raise
        date = validation.validate_date(sys.argv[1])
        if not date:
            raise
        codes = validation.validate_codes(sys.argv[2:])
        if codes[0] == []:
            raise
        code_list = api.ApiGetAndParse(date).get_required_currensies(codes[0])
        db.Inserter(date, code_list).insert_date()
        db.Inserter(date, code_list).insert_rates()
        db.Reader(date).read()
    except Exception as e:
        print(e)
    sys.exit()


if __name__ == '__main__':
    main()
