from enum import Enum

class PopupError(str, Enum):
    MISSING_PARAMETERS = "Brakuje parametrów\n"
    EMPTY_CURRENCY_LIST = "Nie podano żadnych walut\n"
    NO_CURRENCY_PAIR = "Brakuje waluty do pary\n"
    NOT_UNIQUE_CURRENCIES = "Waluty w parze są takie same\n"
    DEND_BEFORE_DSTART = "Data początkowa jest datą pózniejszą niż końcowa\n"
    NOT_EXIST_DATE = "Data początkowa jest datą która jeszcze nie nastąpiła\n"
    NO_DATA_FOR_DATE = "Brak danych dla wybranej daty\n"
    UNEXPECTED_ERROR = "Niespodziewany błąd\n"