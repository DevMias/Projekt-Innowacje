import pandas as pd
import datetime
import csv
from csv import Error as csvError
from urllib.error import URLError

from datetime import datetime as dt

from PyQt5.QtCore import QDate

from backend.AutoEncoder import auto_encoder
from backend.DB_scan import db_scan
from backend.StandardDeviation import standard_deviation
from backend.IsolationForest import isolation_forest
from backend.LocalOutlierFactor import local_outlier
from backend.Majority import majority
from backend.CombinedMethods import all_methods_combined

from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtGui import QIcon

from enums.backend_enums import PopupError
from front.styles import app_logo

'''
https://stooq.pl/q/d/l/?s=[currency1][currency2]&d1=[date_start]&d2=[date_stop]&i=[interval]

currencies:
currency1: eur - euro 
currency2: usd - dollar
eurusd = euro to dollar

date format: yyyymmdd

No date format: (https://stooq.pl/q/d/l/?s=usdpln&i=y) 02-01-1984 to current day

Intervals:
d - day
w - week
m - month
q - quarter
y - year
'''


def return_date(date):
    """
        Args: date (datetime): A datetime object that represents a date.

        Returns:
            -str: Returns a string representation of the date in the format 'YYYYMMDD'.
        Functionality:
            -function takes a datetime object as input and returns a string representation of the date in the format 'YYYYMMDD'.
             used to convert datetime objects to the format used in the dataset.

    """
    month = str(date.date().month())
    day = str(date.date().day())
    if date.date().month() < 10:
        month = "0" + str(date.date().month())
    if date.date().day() < 10:
        day = "0" + str(date.date().day())

    return str(date.date().year()) + month + day


def string_to_date(date):
    """
        Args:
            date (str): A date string in the format 'YYYYMMDD'.

        Returns:
            QDate: Returns a QDate object that represents the date.

        Functionality:
                -function takes a date string in the format 'YYYYMMDD' as input and returns a QDate object that represents the date.
                 It is used to convert date strings in the format used in the dataset to QDate objects, which can be used in PyQt5 for
                 displaying dates.
    """
    return QDate(int(date[:4]), int(date[4:6]), int(date[6:8]))


def create_link(currencies: list, date_start: str, date_stop: str, interval: str) -> list:
    """
        Args:
            -currencies (list of str): A list of currency codes, represented as two-letter strings, for which exchange rate data
            is to be downloaded. The list must contain either two or four currency codes.
            -date_start (str): A string representation of the start date for the exchange rate data, in the format 'YYYY-MM-DD'.
            -date_stop (str): A string representation of the end date for the exchange rate data, in the format 'YYYY-MM-DD'.
            -interval (str): A string that specifies the time interval for the exchange rate data.
        Returns:
                list: Returns a list of one or two Stooq links that can be used to download historical exchange rate data for the
                specified currencies and time period.
        Functionality:
            This function takes a list of currency codes, a start date, an end date, and a time interval as input, and returns a list
            of Stooq links that can be used to download historical exchange rate data for the specified currencies and time period.
            The returned list contains one or two links, depending on whether two or four currency codes were provided.

    """
    if interval == "Dzienny":
        interval = 'd'
    if interval == "Tygodniowy":
        interval = 'w'
    if interval == "Miesięczny":
        interval = 'm'
    if interval == "Kwartalny":
        interval = 'q'
    if interval == "Roczny":
        interval = 'y'

    link1 = "https://stooq.pl/q/d/l/?s=" + currencies[0] + currencies[1] + "&d1=" + date_start + "&d2=" + date_stop + "&i=" + \
           interval

    link2 = ""
    if len(currencies) > 2:
        link2 = "https://stooq.pl/q/d/l/?s=" + currencies[2] + currencies[3] + "&d1=" + date_start + "&d2=" + date_stop + "&i=" + \
                interval

    return [link1, link2] if len(currencies) > 2 else [link1]


def error(text, inform_text="", title="Błąd", icon=QMessageBox.Critical, buttons=QMessageBox.Ok):
    """
        Args:
            -text (str): The main text to be displayed in the error message box.
            -inform_text (str): Optional informative text to be displayed below the main text in the error message box.
            -title (str): Optional title for the error message box. The default value is "Błąd".
            -icon (QMessageBox.Icon): Optional icon to be displayed in the error message box. The default value is
                QMessageBox.Critical.
            -buttons (QMessageBox.StandardButtons): Optional buttons to be displayed in the error message box. The default value
                   is QMessageBox.Ok.

        Returns:
            -int: Returns the button clicked by the user.

        Functionality:
                function displays an error message box with the specified text and icon, and returns the button clicked by the user.
                The default icon is the 'Critical' icon, and the default button is the 'Ok' button. The function also takes an optional
                informative text and title for the message box.
           """
    msg = QMessageBox()
    msg.setWindowIcon(QIcon(app_logo))
    msg.setText(text)
    msg.setInformativeText(inform_text)
    msg.setIcon(icon)
    msg.setStandardButtons(buttons)
    msg.setWindowTitle(title)
    msg.show()
    return msg.exec_()


def check_date(data, date, date_format):
    """
        This function checks the format of the dates in the specified column of a pandas DataFrame, and returns the DataFrame if
        the format is correct. The function takes the DataFrame, the name of the date column, and the expected date format as input.
        The date format should be specified using the strings 'Rok', 'Miesiąc', and 'Dzień' separated by a single separator character.
        If the format is correct, the function also checks that the dates are in chronological order, and displays a warning message
        if they are not.

        Args:
            -data (pd.DataFrame): The pandas DataFrame to be checked.
            -date (str): The name of the column that contains the dates to be checked.
            -date_format (str): A string that specifies the expected date format.

        Returns:
            -pd.DataFrame: Returns the input DataFrame if the date format is correct and the dates are in chronological order.
            Otherwise, the function displays an error or warning message and returns None.

        Functionality:
            This function checks the format of the dates in the specified column of a pandas DataFrame, and returns the DataFrame if
            the format is correct. The function takes the DataFrame, the name of the date column, and the expected date format as input.
            The date format should be specified using the strings 'Rok', 'Miesiąc', and 'Dzień' separated by a single separator character.
            If the format is correct, the function also checks that the dates are in chronological order, and displays a warning message
            if they are not.
    """
    date_as_list = list(data[date][0])

    separator = None

    for c in date_as_list:
        if not c.isnumeric():
            separator = c
            break

    if separator is None:
        error("Błędny format daty", "Dane w kolumnie " + date + " mają nieprawidłowy format")
        return None

    format_string = ""

    year = 0
    month = 0
    day = 0

    for date_f in date_format.split("-"):
        if date_f == "Rok":
            format_string += "%Y"
            year += 1
        if date_f == "Miesiąc":
            format_string += "%m"
            month += 1
        if date_f == "Dzień":
            format_string += "%d"
            day += 1
        format_string += separator

    if year != 1 or month != 1 or day != 1:
        error("Błędny format daty", "Wprowadzono niepoprawny format daty")
        return None

    format_string = format_string[:-1]

    try:
        date_first = dt.strptime(data[date][0], format_string)
        date_last = dt.strptime(data[date][len(data[date]) - 1], format_string)

        if date_first > date_last:
            data = data.reindex(index=data.index[::-1]).reset_index(drop=True)

        dates_in_order = True
        date_first = dt.strptime(data[date][0], format_string)

        for idx in data.index[:-1]:
            date_last = dt.strptime(data[date][idx + 1], format_string)

            if date_first > date_last:
                dates_in_order = False
            date_first = date_last

        if not dates_in_order:
            error("Daty w pliku nie są uporządkowane", title="Uwaga", icon=QMessageBox.Warning)

        return data
    except ValueError:
        error("Błędny format daty", "Format danych w kolumnie " + date + " nie zgadza się z wprowadzonym")
        return None


def download_csv_without_errors(link):
    """
        This function attempts to download a CSV file from the specified link using pandas, and returns the resulting DataFrame
        if the download is successful. If the download fails or the resulting DataFrame is empty or null, the function returns None.

        Args:
            -link (str): A string that contains the URL for the CSV file to be downloaded.

        Returns:
            Union[pd.DataFrame, None]: Returns a pandas DataFrame containing the data from the downloaded CSV file, or None if
            the download failed or the resulting DataFrame is empty or null.

        Functionality:
            -function download a CSV file from the specified link using pandas, and returns the resulting DataFrame
            if the download is successful. If the download fails or the resulting DataFrame is empty or null, the function returns None.
    """
    try:
        dataframe = pd.read_csv(link, sep=',')

        if len(dataframe) <= 1 or dataframe.index.empty:
            return None

        return dataframe
    except:
        return None


def download_csv(filepaths: list, separator=',', from_file=False) -> pd.arrays:
    """
        Args:
            -filepaths (List[str]): A list of strings that contains the file paths or URLs for the CSV files to be downloaded.
            -separator (str): A string that specifies the separator character to be used in the resulting DataFrames. The default
                value is ','.
            -from_file (bool): A boolean that specifies whether the file paths are for local files or URLs. The default value is False.

        Returns:
            -Tuple[Union[List[pd.DataFrame], None], str]: Returns a tuple containing a list of pandas DataFrames, or a value of
            None and a string that specifies the reason for the failure.

        Functionality:
            -function attempts to download one or more CSV files from the specified file paths or URLs using pandas, and returns
            a list of DataFrames containing the data from the downloaded CSV files if the downloads are successful. If any of the
            downloaded DataFrames are empty or null, the function returns a tuple with a value of None and the string "empty". If the
            function encounters a connection error, it returns a tuple with a value of None and the string "connection error". If the
            function encounters an error with the file format or any other type of error, it returns a tuple with a value of None and
            an empty string.
    """
    try:
        dfs = list()
        for i in range(len(filepaths)):
            if from_file:
                f = open(filepaths[i], "r").read()
                sniffer = csv.Sniffer()
                dialect = sniffer.sniff(f)
                separator = dialect.delimiter

            dataframe = pd.read_csv(filepaths[i], sep=separator)

            if len(dataframe) <= 1 or dataframe.index.empty:
                return None, "empty"

            if separator != ',':
                error("Wykryto separator '" + str(separator) + "'", "Pliki wyjściowe będą zawierać separator ','."
                                                                    " Uważaj na nadpisywanie plików.",
                      title="Separator w pliku", icon=QMessageBox.Information)
            dfs.append(dataframe)

        return dfs, ""

    except URLError:
        error("Błąd połączenia z serwerem", "Sprawdź swoje połączenie internetowe")
        return None, "connection error"
    except UnicodeDecodeError:
        if from_file: error("Błedny plik", "Nieprawidłowy format pliku")
        return None, ""
    except csvError:
        if from_file: error("Błedny plik", "Wprowadzony plik jest pusty")
        return None, ""
    except:
        if from_file: error("Błedny plik", "Wprowadzony plik nie jest plikiem zawierającym dane w formacie csv")
        else: error("Błedny plik", "Wprowadzony plik jest pusty")
        return None, ""


def run_method(datas: list, target: str, date: str, method: str, parameter=0):
    """
        Args:
            -datas (List): A list of pandas DataFrames containing the input data.
            -target (str): A string that specifies the name of the column containing the target variable.
            -date (str): A string that specifies the name of the column containing the date variable.
            -method (str): A string that specifies the name of the anomaly detection method to be executed.
            -parameter (Union[int, float]): A numeric parameter that may be required by some of the anomaly detection methods. The default value is 0.
        Returns:
            -pd.DataFrame: Returns a pandas DataFrame containing the results of the specified anomaly detection method.

        Functionality:
            -function executes the specified anomaly detection method on the given input data and returns a pandas DataFrame
            containing the results.
    """
    if method == "Odchylenie standardowe":
        return standard_deviation(datas=datas, target=target, date=date)
    if method == "Grupowanie przestrzenne":
        return db_scan(datas=datas, target=target, date=date, multiplayer=parameter)
    if method == "Las izolacji":
        return isolation_forest(datas=datas, target=target, date=date, contamination=parameter)
    if method == "Lokalna wartość odstająca":
        return local_outlier(datas=datas, target=target, date=date, contamination=parameter)
    if method == "Większościowa":
        return majority(datas=datas, target=target, date=date)
    if method == "Autoenkoder":
        return auto_encoder(datas=datas, target=target, date=date)
    if method == "Wszystkie":
        return all_methods_combined(datas=datas, target=target, date=date)


def input_errors(currency_list: list = None, start_date: QDate = None, stop_date: QDate = None, generate_popup: bool = True):
    ''' This class should always return some kind of error, it is called when csv file is not specified in main.py
        There is a test class for this function in tests.backend_tests.py (feel free to add more tests) and enum class in enums.backend_enums.py'''
    my_errors = ""
    if currency_list is None or stop_date is None or stop_date is None:
        my_errors += PopupError.MISSING_PARAMETERS
    else:
        list_len = len(currency_list)
        if not list_len: my_errors = PopupError.EMPTY_CURRENCY_LIST # check if empty
        elif list_len % 2: my_errors = PopupError.NO_CURRENCY_PAIR  # check if even
        for curr_1, curr_2 in zip(currency_list[::2], currency_list[1::2]): # it will take i and i+1 element of currency_list
            if curr_1 == curr_2: my_errors = PopupError.NOT_UNIQUE_CURRENCIES; break
        if list_len == 4 and currency_list[0:2] == currency_list[2:4]: my_errors = PopupError.NOT_UNIQUE_CURRENCIES # write universally in future

        if start_date.year() > stop_date.year(): my_errors += PopupError.DEND_BEFORE_DSTART
        elif start_date.year() == stop_date.year():
            if start_date.month() > stop_date.month(): my_errors += PopupError.DEND_BEFORE_DSTART
            elif start_date.month() == stop_date.month():
                if start_date.day() > stop_date.day(): my_errors += PopupError.DEND_BEFORE_DSTART
                elif start_date.day() == stop_date.day(): my_errors += PopupError.DEND_BEFORE_DSTART

        if start_date.toPyDate() > datetime.date.today(): my_errors += PopupError.NOT_EXIST_DATE
        elif stop_date.year() < 1970: my_errors += PopupError.NO_DATA_FOR_DATE

    if my_errors == "": my_errors += PopupError.UNEXPECTED_ERROR
    if generate_popup: error("Błedne dane", my_errors)
    return my_errors
