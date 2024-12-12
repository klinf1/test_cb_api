import sys

import api
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
        print(code_list)
    except Exception as e:
        print(e)


if __name__ == '__main__':
    main()
