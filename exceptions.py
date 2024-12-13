class InputError(Exception):
    def __str__(self):
        note = 'Не введены дата и/или список кодов.'
        note += '\nПовторите запуск, указав дату в формате ДД.ММ.ГГГГ'
        note += 'и числовые коды валют (двух- или трехзначные числа)'
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
