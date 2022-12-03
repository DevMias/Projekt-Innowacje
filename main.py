import sys
import webbrowser
import os
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import QAction, qApp, QApplication, QWidget, QPushButton

from backend import backend_functions as backend
from backend import tab_functions as backend_funcs
from backend import graph_preview as backend_graph
from front.styles import *

from front.graph import Graph
import pyqtgraph.exporters as exporters
import pyqtgraph as pg

methods_with_parameter = ["Grupowanie przestrzenne", "Las izolacji", "Lokalna wartość odstająca"]


def clear_layout(layout):
    while layout.count():
        child = layout.takeAt(0)
        if child.widget():
            child.widget().deleteLater()


class Window(QMainWindow):
    def __init__(self, parent=None):
        super(Window, self).__init__(parent, flags=Qt.WindowFlags())
        self.graph_preview = pg.PlotWidget()
        self.plot_variables = {}
        self.important_tabs = []
        self.help_tab = None
        self.settings_tab = None
        self.creators_tab = None
        self.button_settings = backend_funcs.create_button(style=buttonStyleSheet, icon=QIcon(settings_icon),
                                                           min_size=(45, 45), max_size=(45, 45), function=self.settings)
        self.settings_pack = None
        self.read_settings_from_file()
        self.interval_list = ["Dzienny", "Tygodniowy", "Miesięczny", "Kwartalny", "Roczny"]
        self.pack = {}

        # tabs
        self.tabs = QTabWidget(self)
        self.tabs.setStyleSheet(tabStyleSheet)
        self.tabs.setMovable(True)
        self.tabs.setTabsClosable(True)
        self.tabs.setTabShape(1)
        self.tabs.tabCloseRequested.connect(lambda index: self.close_tab(index))
        self.tab_main = QWidget()
        self.tabs.addTab(self.tab_main, "Start")
        self.graphs = {}

        # generate plot button
        self.button_plot = backend_funcs.create_button(text="Wygeneruj wykres", style=buttonStyleSheet,
                                                       min_size=(100, 40), function=self.create_plot)

        # swap currencies button
        self.button_swap = backend_funcs.create_button(style=buttonStyleSheet, icon=QIcon(swap_icon), max_size=(65, 65),
                                                       min_size=(65, 65), function=self.swap_currencies)

        # calendars for setting dates
        self.calendar_start_label = QLabel("Data początkowa")
        self.calendar_start_label.setStyleSheet(labelStyleSheet)
        self.calendar_stop_label = QLabel("Data końcowa")
        self.calendar_stop_label.setStyleSheet(labelStyleSheet)

        self.calendar_start = QtWidgets.QDateEdit()
        self.calendar_start.setCalendarPopup(True)
        self.calendar_start.setStyleSheet(DateEditStyleSheet)
        self.calendar_stop = QtWidgets.QDateEdit()
        self.calendar_stop.setCalendarPopup(True)
        self.calendar_stop.setStyleSheet(DateEditStyleSheet)

        # methods
        self.method_list = ["Odchylenie standardowe", "Grupowanie przestrzenne", "Las izolacji",
                            "Lokalna wartość odstająca", "Autoenkoder", "Większościowa", "Wszystkie"]
        self.method_label = QLabel("Metoda")
        self.method_label.setStyleSheet(labelStyleSheet)
        self.methods = QComboBox()
        self.methods.setStyleSheet(comboBoxStyleSheet)

        # intervals
        self.interval_label = QLabel("Interwał")
        self.interval_label.setStyleSheet(labelStyleSheet)
        self.interval = QComboBox()
        self.interval.setStyleSheet(comboBoxStyleSheet)

        # currencies
        self.currencies_label = QLabel("Waluty")
        self.currencies_label.setStyleSheet(labelStyleSheet)
        self.currencies1 = QComboBox()
        self.currencies1.setStyleSheet(comboBoxStyleSheet)
        self.currencies2 = QComboBox()
        self.currencies2.setStyleSheet(comboBoxStyleSheet)

        self.title_label = QLabel("Tytuł wykresu")
        self.title_label.setStyleSheet(labelStyleSheet)
        self.title = QLineEdit()
        self.title.setStyleSheet(labelStyleSheet)
        self.title.setMaxLength(50)

        # window settings
        self.setMinimumSize(1280, 720)
        self.resize(1280, 720)
        self.setWindowTitle("Detektor anomalii")
        self.setWindowIcon(QIcon(app_logo))
        font_qt = QFont()

        self.alpha = [0, 0]

        font_qt.setFamily("Arial")
        font_qt.setPointSize(30)
        self.init_menu()
        self.layout = QGridLayout()
        self.init_layout()

        self.show()

    def init_menu(self):
        exit_action = QAction('&Zamknij', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.setStatusTip('Wyjdź z aplikacji')
        exit_action.triggered.connect(qApp.quit)

        file_action = QAction('&Otwórz', self)
        file_action.setShortcut('Ctrl+O')
        file_action.triggered.connect(self.file_open)

        graph_action = QAction('&Otwórz graf', self)
        graph_action.triggered.connect(self.graph_from_file)

        help_action = QAction('&Pomoc', self)
        help_action.triggered.connect(self.help)

        creators_action = QAction('&Twórcy', self)
        creators_action.triggered.connect(self.creators)

        menubar = self.menuBar()
        file_menu = menubar.addMenu('&Plik')
        file_menu.addAction(file_action)
        file_menu.addAction(graph_action)
        file_menu.addAction(exit_action)
        menubar.addAction(help_action)
        menubar.addAction(creators_action)

    def init_layout(self):
        clear_layout(self.layout)

        # lists for currencies
        for flag, currency in zip(flag_list, currencies_list):
            self.currencies1.addItem(QIcon(flag), currency)
            self.currencies2.addItem(QIcon(flag), currency)

        # self.currencies1.setCurrentText(self.settings_pack["currencies1"])
        # self.currencies2.setCurrentText(self.settings_pack["currencies2"])

        self.currencies1.setCurrentIndex(int(self.settings_pack["currencies1"]))
        self.currencies2.setCurrentIndex(int(self.settings_pack["currencies2"]))

        if self.settings_pack["date_checkbox"] == "False":
            self.calendar_start.setDate(backend.string_to_date(self.settings_pack["date_start"]))
            self.calendar_stop.setDate(backend.string_to_date(self.settings_pack["date_stop"]))
        else:
            self.calendar_start.setDate(QDate.currentDate().addYears(-1))
            self.calendar_stop.setDate(QDate.currentDate())

        # list for intervals
        interval_image = ["numbers/" + name + ".png" for name in self.interval_list]

        for image, interval in zip(interval_image, self.interval_list):
            self.interval.addItem(QIcon(image), interval)

        # self.interval.setCurrentText(self.settings_pack["intervals"])
        self.interval.setCurrentIndex(int(self.settings_pack["intervals"]))

        # list for methods
        self.method_list.sort()

        for method in self.method_list:
            self.methods.addItem(method)

        # self.methods.setCurrentText(self.settings_pack["methods"])
        self.methods.setCurrentIndex(int(self.settings_pack["methods"]))

        self.plot_variables = {"title": self.title, "currencies": (self.currencies1, self.currencies2),
                               "dates": (self.calendar_start, self.calendar_stop), "interval": self.interval}

        self.currencies1.currentIndexChanged.connect(self.graph_preview_change)
        self.currencies2.currentIndexChanged.connect(self.graph_preview_change)
        self.interval.currentIndexChanged.connect(self.graph_preview_change)
        self.title.textChanged.connect(self.graph_preview_change)
        self.calendar_start.dateChanged.connect(self.graph_preview_change)
        self.calendar_stop.dateChanged.connect(self.graph_preview_change)

        self.graph_preview = backend_graph.create_plot(self.graph_preview, self.plot_variables)

        # main tab layout
        self.tab_main.layout = QGridLayout()
        self.tab_main.layout.setSpacing(10)
        self.tab_main.layout.addWidget(self.title_label, 1, 0, 1, 2)
        self.tab_main.layout.addWidget(self.button_settings, 1, 2, alignment=Qt.AlignRight)
        self.tab_main.layout.addWidget(self.title, 2, 0, 1, 2)
        self.tab_main.layout.addWidget(self.currencies_label, 3, 0, 1, 2)
        self.tab_main.layout.addWidget(self.currencies1, 4, 0, 1, 1)
        self.tab_main.layout.addWidget(self.currencies2, 5, 0, 1, 1)
        self.tab_main.layout.addWidget(self.button_swap, 4, 1, 2, 1)
        self.tab_main.layout.addWidget(self.calendar_start_label, 6, 0, 1, 2)
        self.tab_main.layout.addWidget(self.calendar_start, 7, 0, 1, 2)
        self.tab_main.layout.addWidget(self.calendar_stop_label, 8, 0, 1, 2)
        self.tab_main.layout.addWidget(self.calendar_stop, 9, 0, 1, 2)
        self.tab_main.layout.addWidget(self.interval_label, 10, 0, 1, 2)
        self.tab_main.layout.addWidget(self.interval, 11, 0, 1, 2)
        self.tab_main.layout.addWidget(self.method_label, 12, 0, 1, 2)
        self.tab_main.layout.addWidget(self.methods, 13, 0, 1, 2)
        self.tab_main.layout.addWidget(self.button_plot, 14, 0, 1, 3)
        self.tab_main.layout.addWidget(self.graph_preview, 2, 2, 12, 1)

        self.layout.addWidget(self.tabs)
        self.tab_main.setLayout(self.tab_main.layout)

        ll = QWidget()
        ll.setLayout(self.layout)
        self.setCentralWidget(ll)

    def graph_preview_change(self):
        self.graph_preview = backend_graph.create_plot(self.graph_preview, self.plot_variables)

    def swap_currencies(self):
        tmp = self.currencies1.currentText()
        self.currencies1.setCurrentText(self.currencies2.currentText())
        self.currencies2.setCurrentText(tmp)

    def important_add_tab(self):
        tab = self.tabs.currentWidget()
        if tab not in self.important_tabs:
            self.tabs.setTabIcon(self.tabs.indexOf(tab), QIcon(important_icon))
            self.important_tabs.append(tab)
        else:
            self.tabs.setTabIcon(self.tabs.indexOf(tab), QIcon(not_important_icon))
            self.important_tabs.pop(self.important_tabs.index(tab))

    def close_tab(self, index):
        if not isinstance(index, bool):
            if self.tabs.widget(index) in self.important_tabs:
                pressed = backend.error("Czy chcesz zamknąć ważną kartę?", title="Ważna karta",
                                        icon=QMessageBox.Question,
                                        buttons=QMessageBox.Yes | QMessageBox.No)
                if pressed != QMessageBox.Yes:
                    return

            if self.tabs.indexOf(self.tab_main) == index:
                return

            if self.tabs.indexOf(self.creators_tab) == index:
                self.creators_tab = None

            if self.tabs.indexOf(self.settings_tab) == index:
                self.settings_tab = None

            if self.tabs.indexOf(self.help_tab) == index:
                self.help_tab = None

            self.graphs.pop(self.tabs.widget(index), None)
            self.tabs.removeTab(index)

            return

        current_index = self.tabs.indexOf(self.tabs.currentWidget())
        self.close_tab(current_index)

    def settings(self):
        if self.settings_tab is not None:
            self.tabs.setCurrentIndex(self.tabs.indexOf(self.settings_tab))
            return

        tab, p = backend_funcs.create_settings_tab(self.method_list, self.interval_list, self.close_tab,
                                                   self.save_settings_to_file, self.reset_settings)
        self.settings_pack = p

        self.tabs.addTab(tab, "Ustawienia")
        self.tabs.setCurrentIndex(self.tabs.indexOf(tab))

        self.settings_tab = tab

    def help(self):
        help_file = os.getcwd() + "/help/index.html"
        print(help_file)
        webbrowser.open("file:///"+help_file)
        # if self.help_tab is not None:
        #     self.tabs.setCurrentIndex(self.tabs.indexOf(self.help_tab))
        #     return

        # tab = backend_funcs.create_help_tab(self.close_tab)

        # self.tabs.addTab(tab, "Pomoc")
        # self.tabs.setCurrentIndex(self.tabs.indexOf(tab))

        # self.help_tab = tab

    def creators(self):
        if self.creators_tab is not None:
            self.tabs.setCurrentIndex(self.tabs.indexOf(self.creators_tab))
            return

        tab = backend_funcs.create_creators_tab(self.close_tab)

        self.tabs.addTab(tab, "Twórcy")
        self.tabs.setCurrentIndex(self.tabs.indexOf(tab))

        self.creators_tab = tab

    def save_settings_to_file(self):
        # self.currencies1.setCurrentText(self.settings_pack["currencies1"].currentText())
        # self.currencies2.setCurrentText(self.settings_pack["currencies2"].currentText())
        # self.methods.setCurrentText(self.settings_pack["methods"].currentText())
        # self.interval.setCurrentText(self.settings_pack["intervals"].currentText())

        self.currencies1.setCurrentIndex(self.settings_pack["currencies1"].currentIndex())
        self.currencies2.setCurrentIndex(self.settings_pack["currencies2"].currentIndex())
        self.methods.setCurrentIndex(self.settings_pack["methods"].currentIndex())
        self.interval.setCurrentIndex(self.settings_pack["intervals"].currentIndex())

        if not self.settings_pack["date_checkbox"].isChecked():
            self.calendar_start.setDate(backend.string_to_date(backend.return_date(self.settings_pack["date_start"])))
            self.calendar_stop.setDate(backend.string_to_date(backend.return_date(self.settings_pack["date_stop"])))
        else:
            self.calendar_start.setDate(QDate.currentDate().addYears(-1))
            self.calendar_stop.setDate(QDate.currentDate())
            self.settings_pack["date_start"].setDate(QDate.currentDate().addYears(-1))
            self.settings_pack["date_stop"].setDate(QDate.currentDate())

        # currency1 = "currency1:" + self.settings_pack["currencies1"].currentText() + '\n'
        # currency2 = "currency2:" + self.settings_pack["currencies2"].currentText() + '\n'
        # method = "method:" + self.settings_pack["methods"].currentText() + '\n'
        # interval = "interval:" + self.settings_pack["intervals"].currentText() + '\n'

        currency1 = "currency1:" + str(self.settings_pack["currencies1"].currentIndex()) + '\n'
        currency2 = "currency2:" + str(self.settings_pack["currencies2"].currentIndex()) + '\n'
        method = "method:" + str(self.settings_pack["methods"].currentIndex()) + '\n'
        interval = "interval:" + str(self.settings_pack["intervals"].currentIndex()) + '\n'

        date_start = "date_start:" + backend.return_date(self.settings_pack["date_start"]) + '\n'
        date_stop = "date_stop:" + backend.return_date(self.settings_pack["date_stop"]) + '\n'
        checkbox = "checkbox:" + str(self.settings_pack["date_checkbox"].isChecked()) + '\n'
        settings = [currency1, currency2, method, interval, date_start, date_stop, checkbox]
        open('settings', 'w').writelines(settings)

    def read_settings_from_file(self):
        f = open('settings', "r").readlines()
        settings = []
        for line in f:
            settings.append(line.split(':')[1][:-1])

        self.settings_pack = {"currencies1": settings[0], "currencies2": settings[1],
                              "methods": settings[2], "intervals": settings[3], "date_start": settings[4],
                              "date_stop": settings[5], "date_checkbox": settings[6]}

    def reset_settings(self):
        f = open('default_settings', "r").readlines()
        settings = []
        for line in f:
            settings.append(line.split(':')[1][:-1])

        self.settings_pack = {"currencies1": settings[0], "currencies2": settings[1],
                              "methods": settings[2], "intervals": settings[3], "date_start": settings[4],
                              "date_stop": settings[5], "date_checkbox": settings[6]}

        currency1 = "currency1:" + self.settings_pack["currencies1"] + '\n'
        currency2 = "currency2:" + self.settings_pack["currencies2"] + '\n'
        method = "method:" + self.settings_pack["methods"] + '\n'
        interval = "interval:" + self.settings_pack["intervals"] + '\n'
        date_start = "date_start:" + self.settings_pack["date_start"] + '\n'
        date_stop = "date_stop:" + self.settings_pack["date_stop"] + '\n'
        checkbox = "checkbox:" + self.settings_pack["date_checkbox"] + '\n'
        settings_new = [currency1, currency2, method, interval, date_start, date_stop, checkbox]
        open('settings', 'w').writelines(settings_new)

        self.close_tab(False)
        self.settings()

    def graph_from_file(self):
        file, _ = QFileDialog.getOpenFileName(self, "Detektor anomalii", "", "CSV Files (*.csv *.txt)",
                                              options=QFileDialog.Options())
        if file is None or file == "":
            return

        csv, error = backend.download_csv(file)

        if error == "empty":
            backend.error("Błedny plik", "Wprowadzony plik jest pusty lub posiada zbyt mało danych")

        if csv is None:
            return

        pack = {"method": "", "csv": csv, "title": "Wykres " + file.split('/')[-1], "date": "Date",
                "target": "Exchange"}

        self.pack_data(pack)

    def file_open(self):
        file, _ = QFileDialog.getOpenFileName(self, "Detektor anomalii", "", "CSV Files (*.csv *.txt)",
                                              options=QFileDialog.Options())
        if file is None or file == "":
            return

        tab, pack = backend_funcs.create_graph_tab(close=self.close_tab, pack_fun=self.pack_data, file=file,
                                                   methods_list=self.method_list, important=self.important_add_tab)

        if tab is None or pack is None:
            return

        self.pack[tab] = pack
        self.tabs.addTab(tab, file.split('/')[-1])
        self.tabs.setCurrentIndex(self.tabs.indexOf(tab))

    def pack_data(self, pack):
        from_file = True

        if pack is False:
            pack = self.pack[self.tabs.currentWidget()]
            from_file = False
            method = pack["method"].currentText()
            title = pack["title"].text()
            date = pack["date"].currentText()
            target = pack["target"].currentText()
            csv = pack["csv"]
            date_format = pack["format1"].currentText() + '-' + pack["format2"].currentText() + '-' + pack[
                "format3"].currentText()
            csv = backend.check_date(csv, date, date_format)

            if csv is None:
                return
        else:
            method = pack["method"]
            title = pack["title"]
            date = pack["date"]
            target = pack["target"]
            csv = pack["csv"]

        columns = csv.columns.tolist()
        errors = ""
        make_graph = True

        if date in columns and target in columns:
            for number in csv[target]:
                if not isinstance(number, (float, int)) or isinstance(number, bool):
                    backend.error("Błędne dane", "Dane w kolumnie " + target + " muszą być liczbą rzeczywistą")
                    return
            for date1 in csv[date]:
                if not isinstance(date1, str) or isinstance(date1, bool):
                    backend.error("Błędne dane", "Dane w kolumnie " + date + " muszą być w formie tekstowej")
                    return
            if from_file and 'Anomaly' in columns:
                method = "other"
                for boolean in csv['Anomaly']:
                    if not isinstance(boolean, bool):
                        backend.error("Błędne dane", "Dane w kolumnie Anomaly muszą być wartościami True lub False")
                        return
            if from_file:
                for i in range(1, 6):
                    if method == "other":
                        break
                    name = 'Anomaly_' + str(i)
                    if from_file and name in columns:
                        method = "Wszystkie"
                        for boolean in csv[name]:
                            if not isinstance(boolean, bool):
                                backend.error("Błędne dane", "Dane w kolumnie " + name +
                                              " muszą być wartościami True lub False")
                                return
                    else:
                        make_graph = False
            if make_graph:
                self.create_graph(csv=csv, method=method, date=date, target=target, title=title,
                                  with_anomalies=from_file)
                return

        if date not in columns:
            errors += "Kolumna " + date + " nie istnieje w podanych danych.\n"
        if target not in columns:
            errors += "Kolumna " + target + " nie istnieje w podanych danych.\n"

        if method != "Wszystkie":
            if from_file and 'Anomaly' not in columns:
                errors += "Kolumna Anomaly nie istnieje w podanych danych.\n"
        else:
            for i in range(1, 6):
                name = 'Anomaly_' + str(i)
                if from_file and name not in columns:
                    errors += "Kolumna " + name + " nie istnieje w podanych danych.\n"

        backend.error("Błędne nazwy kolumn", errors)

    def download_data(self):
        pressed = backend.error("Czy chcesz pobrać dane o anomaliach?", icon=QMessageBox.Question,
                                buttons=QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel, title="Dane")

        graph = self.graphs[self.tabs.currentWidget()]

        data = graph.anomalies_to_download[graph.data_indexes[0]:graph.data_indexes[1]]

        if pressed == QMessageBox.No:
            if graph.method == "Wszystkie":
                for anomalies in graph.anomalies_list:
                    data = data.drop(anomalies, axis=1)
            else:
                data = data.drop("Anomaly", axis=1)
        elif pressed == QMessageBox.Cancel:
            return

        file, _ = QFileDialog.getSaveFileName(self, "Detektor anomalii", "anomaly detection data",
                                              "CSV Files (*.csv);;Text Files(*.txt)", options=QFileDialog.Options())

        if file == "" or data is None:
            return

        try:
            data.to_csv(file, index=False)
        except PermissionError:
            backend.error("Brak dostępu do lokalizacji pliku", "Sprawdź czy plik jest zamknięty jeśli istnieje.")

    def download_graph(self):
        graph = self.graphs[self.tabs.currentWidget()]
        plt = graph.graph

        exporter = exporters.ImageExporter(plt.plotItem)
        exporter.parameters()['width'] = 1920

        file, _ = QFileDialog.getSaveFileName(self, "Detektor anomalii", "anomaly detection plot",
                                              "PNG Files (*.png);;JPEG Files(*.jpg)", options=QFileDialog.Options())

        if file == "":
            return

        try:
            exporter.export(file)
        except PermissionError:
            backend.error("Brak dostępu do lokalizacji pliku", "Sprawdź czy plik jest zamknięty jeśli istnieje.")

    def create_plot(self):
        date = "Data"
        target = "Zamkniecie"

        date_start = backend.return_date(self.calendar_start)
        date_stop = backend.return_date(self.calendar_stop)
        interval = self.interval.currentText()
        method = self.methods.currentText()
        currency1 = self.currencies1.currentText()[:3]
        currency2 = self.currencies2.currentText()[:3]
        title = self.title.text()
        if title == "":
            title = currency1 + "/" + currency2

        link = backend.create_link(currency1, currency2, date_start, date_stop, interval)
        csv, error = backend.download_csv(link)

        if error == "connection error":
            return

        if csv is None:
            backend.input_errors(currency1, currency2, self.calendar_start.date(), self.calendar_stop.date())
        else:
            self.create_graph(csv=csv, method=method, date=date, target=target, title=title, currency1=currency1,
                              currency2=currency2)

    def create_graph(self, csv, method, date, target, title="", currency1="", currency2="", with_anomalies=False):
        tab = QWidget()
        tab.layout = QVBoxLayout()
        horizontal_layout = QHBoxLayout()
        graph_settings_layout = QHBoxLayout()

        button_data = backend_funcs.create_button(style=buttonStyleSheet, max_size=(185, 50), text="Pobierz dane",
                                                  function=self.download_data)

        button_important = backend_funcs.create_button(style=buttonStyleSheet, icon=QIcon(important_icon),
                                                       function=self.important_add_tab, max_size=(40, 40))

        button_graph = backend_funcs.create_button(style=buttonStyleSheet, text="Zapisz", max_size=(185, 50),
                                                   function=self.download_graph)

        button_close = backend_funcs.create_button(style=buttonStyleSheet, max_size=(40, 40), icon=QIcon(close_icon),
                                                   function=self.close_tab)

        refresh_checkbox = QCheckBox()
        refresh_checkbox.setText("Odświeżaj anomalie")
        refresh_checkbox.setChecked(True)

        button_refresh = backend_funcs.create_button(style=buttonStyleSheet, max_size=(185, 50), text="Odśwież")

        button_reset_graph = backend_funcs.create_button(style=buttonStyleSheet, max_size=(185, 50), text="Resetuj")

        button_flip = backend_funcs.create_button(style=buttonStyleSheet, max_size=(185, 50), text="Zamień waluty")

        slider = QSlider(Qt.Horizontal)
        slider.setFocusPolicy(Qt.StrongFocus)
        slider.setTickPosition(QSlider.TicksBothSides)
        slider.setTickInterval(10)
        slider.setSingleStep(1)
        slider.setRange(1, 100)

        label = QLabel()
        label.setStyleSheet(labelStyleSheet)
        horizontal_layout.addWidget(label, alignment=Qt.Alignment())
        horizontal_layout.addWidget(button_graph, alignment=Qt.Alignment())
        horizontal_layout.addWidget(button_data, alignment=Qt.Alignment())
        horizontal_layout.addWidget(button_important, alignment=Qt.Alignment())
        horizontal_layout.addWidget(button_close, alignment=Qt.Alignment())
        tab.layout.addLayout(horizontal_layout)

        slider_label = QLabel("Czułość metody")
        slider_label.setStyleSheet(labelStyleSheet)

        date_label = QLabel("Data: ")
        date_label.setStyleSheet(labelStyleSheet)

        value_label = QLabel("Wartość: ")
        value_label.setStyleSheet(labelStyleSheet)

        button_reset = backend_funcs.create_button(style=buttonStyleSheet, min_size=(110, 40), text="Reset")

        if with_anomalies:
            self.tabs.addTab(tab, title)
        else:
            self.tabs.addTab(tab, method + " " + title)

        new_graph = Graph(method=method, csv=csv, date=date, target=target, currency1=currency1,
                          currency2=currency2, label=label, slider=slider, slider_label=slider_label,
                          checkbox=refresh_checkbox, date_label=date_label, value_label=value_label, title=title,
                          with_anomalies=with_anomalies)

        tab.layout.addWidget(new_graph.graph, alignment=Qt.Alignment())
        if not with_anomalies:
            tab.layout.addWidget(refresh_checkbox, alignment=Qt.Alignment())
            graph_settings_layout.addWidget(button_flip, alignment=Qt.Alignment())
            graph_settings_layout.addWidget(button_refresh, alignment=Qt.Alignment())
            graph_settings_layout.addWidget(button_reset_graph, alignment=Qt.Alignment())
            graph_settings_layout.addWidget(QLabel(" "), alignment=Qt.Alignment())
            graph_settings_layout.addWidget(date_label, alignment=Qt.Alignment())
            graph_settings_layout.addWidget(value_label, alignment=Qt.Alignment())
            tab.layout.addLayout(graph_settings_layout)

            if method in methods_with_parameter:
                slider_layout = QHBoxLayout()
                slider_layout.addWidget(slider_label, alignment=Qt.Alignment())
                slider_layout.addWidget(slider, alignment=Qt.Alignment())
                slider_layout.addWidget(button_reset, alignment=Qt.Alignment())
                button_reset.clicked.connect(new_graph.reset_slider)
                tab.layout.addLayout(slider_layout)

        button_flip.clicked.connect(new_graph.flip)
        slider.valueChanged.connect(new_graph.update_graph)
        button_refresh.clicked.connect(new_graph.refresh_graph)
        button_reset_graph.clicked.connect(new_graph.reset_graph)
        tab.setLayout(tab.layout)

        self.graphs[tab] = new_graph
        self.tabs.setCurrentIndex(self.tabs.indexOf(tab))


def main():
    app = QApplication(sys.argv)
    ex = Window()
    ex.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
