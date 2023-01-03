import unittest

from PyQt5.QtCore import QDate
from backend.backend_functions import input_errors
from enums.backend_enums import PopupError

class Test__input_errors(unittest.TestCase):
    def test__missing_parameters(self):
        self.assertEqual(input_errors(None, None, None, generate_popup=False), PopupError.MISSING_PARAMETERS)
        self.assertEqual(input_errors(None, QDate.currentDate(), None, generate_popup=False), PopupError.MISSING_PARAMETERS)
        self.assertEqual(input_errors(["USD", "PLN", "CHF", "GBP"], QDate.currentDate(), None, generate_popup=False), PopupError.MISSING_PARAMETERS)
    def test__empty_currency_list(self):
        self.assertEqual(input_errors([], QDate.currentDate(), QDate.currentDate().addDays(1), generate_popup=False), PopupError.EMPTY_CURRENCY_LIST)
    def test__no_currency_pair(self):
        self.assertEqual(input_errors(["USD", "PLN", "CHF"], QDate.currentDate(), QDate.currentDate().addDays(1), generate_popup=False), PopupError.NO_CURRENCY_PAIR)
        self.assertEqual(input_errors(["USD"], QDate.currentDate(), QDate.currentDate().addDays(1), generate_popup=False), PopupError.NO_CURRENCY_PAIR)
    def test__not_unique_currencies(self):
        self.assertEqual(input_errors(["PLN", "PLN"], QDate.currentDate(), QDate.currentDate().addDays(1), generate_popup=False), PopupError.NOT_UNIQUE_CURRENCIES)
        self.assertEqual(input_errors(["PLN", "PLN", "USD", "CHF"], QDate.currentDate(), QDate.currentDate().addDays(1), generate_popup=False), PopupError.NOT_UNIQUE_CURRENCIES)
        self.assertEqual(input_errors(["USD", "CHF", "PLN", "PLN"], QDate.currentDate(), QDate.currentDate().addDays(1), generate_popup=False), PopupError.NOT_UNIQUE_CURRENCIES)
        self.assertEqual(input_errors(["USD", "USD", "USD", "USD"], QDate.currentDate(), QDate.currentDate().addDays(1), generate_popup=False), PopupError.NOT_UNIQUE_CURRENCIES)
        self.assertEqual(input_errors(["USD", "PLN", "USD", "PLN"], QDate.currentDate(), QDate.currentDate().addDays(1), generate_popup=False), PopupError.NOT_UNIQUE_CURRENCIES)
        self.assertEqual( input_errors(["USD", "PLN", "USD", "PLN"], QDate.currentDate(), QDate.currentDate().addDays(1), generate_popup=False), PopupError.NOT_UNIQUE_CURRENCIES)
    def test__dend_before_dstart(self):
        self.assertEqual(input_errors(["USD", "PLN", "PLN", "USD"], start_date=QDate(2022, 2, 20), stop_date=QDate(2021, 2, 20), generate_popup=False), PopupError.DEND_BEFORE_DSTART)
        self.assertEqual(input_errors(["USD", "PLN", "PLN", "USD"], start_date=QDate(2022, 4, 20), stop_date=QDate(2022, 2, 20), generate_popup=False), PopupError.DEND_BEFORE_DSTART)
        self.assertEqual(input_errors(["USD", "PLN", "PLN", "USD"], start_date=QDate(2022, 2, 26), stop_date=QDate(2022, 2, 20), generate_popup=False), PopupError.DEND_BEFORE_DSTART)
    def test__not_exist_date(self):
        self.assertEqual(input_errors(["USD", "PLN", "PLN", "USD"], start_date=QDate(2023, 2, 20), stop_date=QDate(2023, 2, 25), generate_popup=False), PopupError.NOT_EXIST_DATE)
    def test__no_data_for_date(self):
        self.assertEqual(input_errors(["USD", "PLN", "PLN", "USD"], start_date=QDate(1960, 2, 20), stop_date=QDate(1960, 2, 25), generate_popup=False), PopupError.NO_DATA_FOR_DATE)
    def test__unexpected_error(self):
        self.assertEqual(input_errors(["USD", "PLN", "PLN", "USD"], QDate.currentDate(), QDate.currentDate().addDays(1), generate_popup=False), PopupError.UNEXPECTED_ERROR)

if __name__ == '__main__':
    unittest.main()