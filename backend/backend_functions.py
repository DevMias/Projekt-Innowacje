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
    month = str(date.date().month())
    day = str(date.date().day())
    if date.date().month() < 10:
        month = "0" + str(date.date().month())
    if date.date().day() < 10:
        day = "0" + str(date.date().day())

    return str(date.date().year()) + month + day


def string_to_date(date):
    return QDate(int(date[:4]), int(date[4:6]), int(date[6:8]))


def create_link(currency1: str, currency2: str, date_start: str, date_stop: str, interval: str) -> str:
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
    try:
        dataframe = pd.read_csv(link, sep=',')

        if len(dataframe) <= 1 or dataframe.index.empty:
            return None

        return dataframe
    except:
        return None


def download_csv(filepath: str, separator=',', from_file=False) -> pd.arrays:
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
    if method == "Odchylenie standardowe":
        return standard_deviation(data, target, date)
    if method == "Grupowanie przestrzenne":
        return db_scan(data, target, date, parameter)
    if method == "Las izolacji":
        return isolation_forest(data, target, date, parameter)
    if method == "Lokalna wartość odstająca":
        return local_outlier(data1=data, target=target, date=date, contamination=parameter)
    if method == "Większościowa":
        return majority(data, target, date)
    if method == "Autoenkoder":
        return auto_encoder(data, target, date)
    if method == "Wszystkie":
        return all_methods_combined(data1=data, target=target, date=date)


def input_errors(currency1, currency2, start_date, stop_date):
    my_errors = ""

    if currency1 == currency2:
        my_errors = "Podane waluty są takie same\n"

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
