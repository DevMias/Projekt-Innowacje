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
    It takes a date object and returns a string of the date in the format YYYYMMDD

    :param date: the date you want to get the data for
    :type QDateEdit
    :return: A string of the date in the format YYYYMMDD
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
    It takes a string in the format YYYYMMDD and returns a QDate object

    :param date: The date to be converted
    :return: A QDate object.
    """
    return QDate(int(date[:4]), int(date[4:6]), int(date[6:8]))


def create_link(currency1: str, currency2: str, date_start: str, date_stop: str, interval: str) -> str:
    """
    It creates a link to the stooq.pl website, which contains the data
    we want to download

    :param currency1: str - the first currency
    :type currency1: str
    :param currency2: str - the second currency
    :type currency2: str
    :param date_start: the date from which you want to start downloading data
    :type date_start: str
    :param date_stop: the last date of the data you want to download
    :type date_stop: str
    :param interval: d - daily, w - weekly, m - monthly, q - quarterly, y - yearly
    :type interval: str
    :return: It is a link to the website with the data.
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

    link = "https://stooq.pl/q/d/l/?s=" + currency1 + currency2 + "&d1=" + date_start + "&d2=" + date_stop + "&i=" + \
           interval

    return link


def error(text, inform_text="", title="Błąd", icon=QMessageBox.Critical, buttons=QMessageBox.Ok):
    # TODO maybe we should rename this function to message_popup or sth?
    """
    Called when user want to close importatn tab via 'X' on tab or 'X' button
    It creates a message box with the given parameters

    :param text: The main text of the message box
    :param inform_text: The text that is displayed below the main text
    :param title: The title of the message box, defaults to Błąd (optional)
    :param icon: QMessageBox.Critical, QMessageBox.Information, QMessageBox.Question, QMessageBox.Warning
    :param buttons: QMessageBox.Ok, QMessageBox.Cancel, QMessageBox.Yes, QMessageBox.No, QMessageBox.Abort,
    QMessageBox.Retry, QMessageBox.Ignore
    :return: The return value is the standard button enum value of the button that was clicked.
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
    It checks if the dates in the file are in the correct order and if they are in the correct format

    :param data: the dataframe
    :param date: name of the column with dates
    :param date_format: a string containing the format of the date, e.g. "Rok-Miesiąc-Dzień"
    :return: The dataframe with the date column in the correct order.
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
    It tries to download a CSV file from a link, and if it fails, it returns None

    :param link: the link to the csv file
    :return: A dataframe
    """
    try:
        dataframe = pd.read_csv(link, sep=',')

        if len(dataframe) <= 1 or dataframe.index.empty:
            return None

        return dataframe
    except:
        return None


def download_csv(filepath: str, separator=',', from_file=False) -> pd.arrays:
    """
    > This function downloads a csv file from a url or reads it from a file and returns a pandas dataframe

    :param filepath: The path to the file you want to download
    :type filepath: str
    :param separator: the separator used in the csv file, defaults to , (optional)
    :param from_file: if True, the filepath is a filepath to a file that contains a list of filepaths to the csv files to be
    downloaded, defaults to False (optional)
    """
    try:
        if from_file:
            f = open(filepath, "r").read()
            sniffer = csv.Sniffer()
            dialect = sniffer.sniff(f)
            separator = dialect.delimiter

        dataframe = pd.read_csv(filepath, sep=separator)

        if len(dataframe) <= 1 or dataframe.index.empty:
            return None, "empty"

        if separator != ',':
            error("Wykryto separator '" + str(separator) + "'", "Pliki wyjściowe będą zawierać separator ','."
                                                                " Uważaj na nadpisywanie plików.",
                  title="Separator w pliku", icon=QMessageBox.Information)

        return dataframe, ""

    except URLError:
        error("Błąd połączenia z serwerem", "Sprawdź swoje połączenie internetowe")
        return None, "connection error"
    except UnicodeDecodeError:
        if from_file:
            error("Błedny plik", "Nieprawidłowy format pliku")
        return None, ""
    except csvError:
        if from_file:
            error("Błedny plik", "Wprowadzony plik jest pusty")
        return None, ""
    except:
        if from_file:
            error("Błedny plik", "Wprowadzony plik nie jest plikiem zawierającym dane w formacie csv")
        return None, ""


def run_method(data: pd.arrays, target: str, date: str, method: str, parameter=0):
    """
    This function takes in a dataframe, a target variable, a date, a method, and a parameter, and returns a dataframe with
    the predicted values for the target variable.

    :param data: the dataframe that contains the data
    :type data: pd.arrays
    :param target: the name of the target variable
    :type target: str
    :param date: the date of the data
    :type date: str
    :param method: the method to be used for the analysis
    :type method: str
    :param parameter: the parameter for the method, if it has one, defaults to 0 (optional)
    """
    if method == "Odchylenie standardowe":
        return standard_deviation(data, target, date)
    if method == "Grupowanie przestrzenne":
        return db_scan(data, target, date, parameter)
    if method == "Las izolacji":
        return isolation_forest(data, target, date, parameter)
    if method == "Lokalna wartość odstająca":
        return local_outlier(data, target, date, parameter)
    if method == "Większościowa":
        return majority(data, target, date)
    if method == "Autoenkoder":
        return auto_encoder(data, target, date)
    if method == "Wszystkie":
        return all_methods_combined(data, target, date)


def input_errors(currency1, currency2, start_date, stop_date):
    """
    This function checks if the input is valid.

    :param currency1: The first currency
    :param currency2: The second currency
    :param start_date: The start date of the data you want to pull
    :param stop_date: the date you want to stop at
    """
    my_errors = ""

    if currency1 == currency2:
        my_errors = "Podane waluty są takie same\n"

    # TODO subtraction of QDate object may simplify if's ?
    if start_date.year() > stop_date.year():
        my_errors += "Data początkowa jest datą pózniejszą niż końcowa\n"
    elif start_date.year() == stop_date.year():
        if start_date.month() > stop_date.month():
            my_errors += "Data początkowa jest datą pózniejszą niż końcowa\n"
        elif start_date.month() == stop_date.month():
            if start_date.day() > stop_date.day():
                my_errors += "Data początkowa jest datą pózniejszą niż końcowa\n"
            elif start_date.day() == stop_date.day():
                my_errors += "Data początkowa jest identyczna jak końcowa\n"

    if start_date.toPyDate() > datetime.date.today():
        my_errors += "Data początkowa jest datą która jeszcze nie nastąpiła\n"

    if my_errors == "" or stop_date.year() < 1970:
        my_errors += "Brak danych dla wybranej daty\n"

    error("Błedne dane", my_errors)
