import sys
import webbrowser
import os

import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'
import numpy as np
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import QAction, qApp, QApplication, QWidget, QCalendarWidget, QCheckBox
from backend import backend_functions as backend, differential_analysis
from backend import tab_functions as backend_funcs
from backend import graph_preview as backend_graph
from front.styles import *
from front.graph import Graph
import pyqtgraph.exporters as exporters
import pyqtgraph as pg


methods_with_parameter = ["Grupowanie przestrzenne", "Las izolacji", "Lokalna wartość odstająca"]

# needed for csv handling
expected_columns = {
            'single_without_anomaly': ['Date', 'Exchange'],
            'single_with_anomaly': ['Date', 'Exchange', 'Anomaly'],
            'single_with_anomaly_all': ['Date', 'Exchange', 'Anomaly_1', 'Anomaly_2', 'Anomaly_3', 'Anomaly_4', 'Anomaly_5'],
            'multiple_without_anomaly': ['Date', 'Exchange-1', 'Exchange-2'],
            'multiple_with_anomaly': ['Date', 'Exchange-1', 'Anomaly-1', 'Exchange-2', 'Anomaly-2'],
            'multiple_with_anomaly_all': ['Date', 'Exchange-1', 'Anomaly_1-1', 'Anomaly_2-1', 'Anomaly_3-1', 'Anomaly_4-1', 'Anomaly_5-1', 'Exchange-2', 'Anomaly_1-2', 'Anomaly_2-2', 'Anomaly_3-2', 'Anomaly_4-2', 'Anomaly_5-2']
        }


def clear_layout(layout):
    while layout.count():
        child = layout.takeAt(0)
        if child.widget():
            child.widget().deleteLater()


class Calendar(QCalendarWidget):
    def __init__(self, parent=None):
        super(Calendar, self).__init__(parent)
        self.setGridVisible(True)
        self.setStyleSheet(calendarStyleSheet)


class Window(QMainWindow):
    def __init__(self, parent=None):
        super(Window, self).__init__(parent, flags=Qt.WindowFlags())

        self.differential = False

        self.graph_preview_top = pg.PlotWidget()
        self.graph_preview_bottom = pg.PlotWidget()
        self.top_plot_variables = {}
        self.bottom_plot_variables = {}
        self.important_tabs = []
        self.help_tab = None
        self.settings_tab = None
        self.creators_tab = None
        self.button_settings = backend_funcs.create_button(style=buttonStyleSheet, icon=QIcon(settings_icon),
                                                           min_size=(45, 45), max_size=(45, 45), function=self.settings)
        # self.setObjectName('testowe_id')
        self.settings_pack = None
        self.read_settings_from_file()
        self.interval_list = ["Dzienny", "Tygodniowy", "Miesięczny", "Kwartalny", "Roczny"]
        self.pack = {}
        # tabs
        self.tabs = QTabWidget(self)
        # self.tabs.setFixedSize(800, 600) # dla testow
        self.tabs.setStyleSheet(mainTabStyleSheet)
        self.tabs.setMovable(True)
        self.tabs.setTabsClosable(True)
        self.tabs.setTabShape(0)  # to mozna zmienic
        self.tabs.tabCloseRequested.connect(lambda index: self.close_tab(index))
        self.tab_main = QWidget()
        self.tabs.addTab(self.tab_main, "Start")
        self.graphs = {}

        # generate plot button
        self.button_plot = backend_funcs.create_button(text="Wygeneruj wykresy", style=generatePlotButtonStyleSheet,
                                                       function=self.create_plot)
        self.button_plot.setFixedWidth(300)

        # swap currencies_bottom button
        self.swap_currencies_bottom = backend_funcs.create_button(style=swapButtonStyleSheet, icon=QIcon(swap_icon),
                                                       function=self.swap_currencies)
        # swap currencies_top button
        self.swap_currencies_top = backend_funcs.create_button(style=swapButtonStyleSheet, icon=QIcon(swap_icon),
                                                       function=self.swap_currencies2)

        self.swap_currencies_bottom.clicked.connect(self.swap_clicked_bottom)
        self.swap_currencies_top.clicked.connect(self.swap_clicked_top)

        # calendars for setting dates
        self.calendar_start_label = QLabel("Data początkowa")
        self.calendar_start_label.setStyleSheet(labelStyleSheet)
        self.calendar_start_label.setObjectName("graph_fields")
        self.calendar_stop_label = QLabel("Data końcowa")
        self.calendar_stop_label.setStyleSheet(labelStyleSheet)
        self.calendar_stop_label.setObjectName("graph_fields")

        calendar_start = backend_funcs.create_calendar(Calendar)
        calendar_stop = backend_funcs.create_calendar(Calendar)

        self.calendar_start = QtWidgets.QDateEdit()
        self.calendar_start.setCalendarPopup(True)
        self.calendar_start.setDisplayFormat("dd-MM-yyyy")
        self.calendar_start.setStyleSheet(DateEditStyleSheet)
        self.calendar_start.setCalendarWidget(calendar_start)

        self.calendar_stop = QtWidgets.QDateEdit()
        self.calendar_stop.setCalendarPopup(True)
        self.calendar_stop.setDisplayFormat("dd-MM-yyyy")
        self.calendar_stop.setStyleSheet(DateEditStyleSheet)
        self.calendar_stop.setCalendarWidget(calendar_stop)

        # methods
        self.method_list = ["Odchylenie standardowe", "Grupowanie przestrzenne", "Las izolacji",
                            "Lokalna wartość odstająca", "Autoenkoder", "Większościowa", "Wszystkie"]
        self.method_label = QLabel("Metoda")
        self.method_label.setStyleSheet(labelStyleSheet)
        self.method_label.setObjectName("graph_fields")
        self.methods = QComboBox()
        self.methods.setStyleSheet(comboBoxStyleSheet)
        self.methods.setObjectName("graph_fields")

        # intervals
        self.interval_label = QLabel("Interwał")
        self.interval_label.setStyleSheet(labelStyleSheet)
        self.interval_label.setObjectName("graph_fields")
        self.interval = QComboBox()
        self.interval.setStyleSheet(comboBoxStyleSheet)

        # currencies_bottom
        self.currencies_bottom_label = QLabel("Waluty")
        self.currencies_bottom_label.setObjectName("graph_fields")
        self.currencies_bottom_label.setStyleSheet(labelStyleSheet)
        self.currencies_bottom_list1 = QComboBox()
        self.currencies_bottom_list1.setStyleSheet(comboBoxStyleSheet)
        self.currencies_bottom_list1.setObjectName("graph_fields")
        # self.currencies_bottom_list1.currentIndexChanged.connect(self.change_label_bottom)
        self.currencies_bottom_list2 = QComboBox()
        self.currencies_bottom_list2.setObjectName("graph_fields")
        self.currencies_bottom_list2.setStyleSheet(comboBoxStyleSheet)
        # self.currencies_bottom_list2.currentIndexChanged.connect(self.change_label_bottom)

        # checkbox for currency
        self.checkbox = QCheckBox("Wyłącz", self)
        self.checkbox.setChecked(True)
        self.checkbox.setObjectName("checkbox")
        self.checkbox.setStyleSheet(checkboxStyleSheet)
        self.checkbox.clicked.connect(self.checkbox_clicked)

        # currencies top
        self.currencies_top_label = QLabel("Waluty")
        self.currencies_top_label.setObjectName("graph_fields")
        self.currencies_top_label.setStyleSheet(labelStyleSheet)
        self.currencies_top_list1 = QComboBox()
        self.currencies_top_list1.setStyleSheet(comboBoxStyleSheet)
        self.currencies_top_list1.setObjectName("graph_fields")
        # self.currencies_top_list1.currentIndexChanged.connect(self.change_label_top)
        self.currencies_top_list2 = QComboBox()
        self.currencies_top_list2.setObjectName("graph_fields")
        self.currencies_top_list2.setStyleSheet(comboBoxStyleSheet)
        # self.currencies_bottom_list2.currentIndexChanged.connect(self.change_label_top)

        self.title_top = QLineEdit()
        self.title_top.setFixedWidth(400)
        self.title_top.setStyleSheet(labelStyleSheet)
        self.title_top.setMaxLength(50)
        self.title_top.setObjectName("title_top")

        self.title_bottom = QLineEdit()
        self.title_bottom.setFixedWidth(400)
        self.title_bottom.setStyleSheet(labelStyleSheet)
        self.title_bottom.setMaxLength(50)
        self.title_bottom.setObjectName("title_bottom")

        # window settings
        self.setMinimumSize(1280, 760)
        self.resize(1280, 760)
        self.setWindowTitle("Detektor anomalii")
        self.setWindowIcon(QIcon(app_logo))
        self.setStyleSheet(windowStyleSheet)
        # font_qt = QFont() # ustawienie fonta, ale nieuzywane

        self.alpha = [0, 0]

        self.init_menu()
        self.layout = QGridLayout()  # 1.layout
        self.init_layout()
        self.show()


    def change_label_top(self): # zmienic funkcje nie dziala w kazdym przypadku
        self.title_top.setPlaceholderText(
            #self.graph_preview_top.text() #to moze dobrze
        )


    def change_label_bottom(self): # zmienic funkcje nie dziala w kazdym przypadku
        self.title_bottom.setPlaceholderText(
            # self.bottom_plot_variables["currencies"][0].currentText()[:3] + '/' +
            # self.bottom_plot_variables["currencies"][1].currentText()[:3]
            #self.graph_preview_bottom.text() #to moze dobrze
        )


    def swap_clicked_top(self):
        if self.title_top.placeholderText() == self.currencies_top_list1.currentText()[:3] + '/' + self.currencies_top_list2.currentText()[:3]:
            self.title_top.setPlaceholderText(
                self.currencies_top_list2.currentText()[:3] + '/' + self.currencies_top_list1.currentText()[:3]
            )
        else:
             self.title_top.setPlaceholderText(
                self.currencies_top_list1.currentText()[:3] + '/' + self.currencies_top_list2.currentText()[:3]
            )


    def swap_clicked_bottom(self):
        if self.title_bottom.placeholderText() == self.currencies_bottom_list1.currentText()[:3] + '/' + self.currencies_bottom_list2.currentText()[:3]:
            self.title_bottom.setPlaceholderText(
                self.currencies_bottom_list2.currentText()[:3] + '/' + self.currencies_bottom_list1.currentText()[:3]
            )
        else:
             self.title_bottom.setPlaceholderText(
                self.currencies_bottom_list1.currentText()[:3] + '/' + self.currencies_bottom_list2.currentText()[:3]
            )


    def checkbox_clicked(self):
        if self.checkbox.isChecked():
            self.graph_preview_bottom.hide()
            self.checkbox.setText("Wyłącz")
            self.currencies_top_list1.setEnabled(True)
            self.currencies_top_list2.setEnabled(True)
            self.swap_currencies_top.setEnabled(True)
            self.currencies_top_list1.setStyleSheet(comboBoxStyleSheet)
            self.currencies_top_list2.setStyleSheet(comboBoxStyleSheet)
            self.currencies_top_label.setStyleSheet(labelStyleSheet)
            self.button_plot.setText("Wygeneruj wykresy")
            self.tab_main.layout.addWidget(self.graph_preview_top, 2, 2, 7, 1)
            self.tab_main.layout.addWidget(self.graph_preview_bottom, 9, 2, 6, 1)
            self.graph_preview_top.show()
            self.graph_preview_bottom.show()
        else:
            self.checkbox.setText("Włącz")
            self.currencies_top_list1.setEnabled(False)
            self.currencies_top_list2.setEnabled(False)
            self.swap_currencies_top.setEnabled(False)
            self.currencies_top_list1.setStyleSheet(comboBoxDisabledStyleSheet)
            self.currencies_top_list2.setStyleSheet(comboBoxDisabledStyleSheet)
            self.currencies_top_label.setStyleSheet(labelDisabledStyleSheet)
            self.button_plot.setText("Wygeneruj wykres")
            self.graph_preview_bottom.hide()
            self.graph_preview_top.hide()
            self.tab_main.layout.addWidget(self.graph_preview_bottom, 2, 2, 14, 1)
            self.graph_preview_bottom.show()


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
            self.currencies_bottom_list1.addItem(QIcon(flag), currency)
            self.currencies_bottom_list2.addItem(QIcon(flag), currency)
            self.currencies_top_list1.addItem(QIcon(flag), currency)
            self.currencies_top_list2.addItem(QIcon(flag), currency)

        self.currencies_bottom_list1.setCurrentIndex(int(self.settings_pack["currencies12"]))
        self.currencies_bottom_list2.setCurrentIndex(int(self.settings_pack["currencies21"]))
        self.currencies_top_list1.setCurrentIndex(int(self.settings_pack["currencies1"]))
        self.currencies_top_list2.setCurrentIndex(int(self.settings_pack["currencies2"]))

        if self.settings_pack["date_checkbox"] == "False":
            self.calendar_start.setDate(backend.string_to_date(self.settings_pack["date_start"]))
            self.calendar_stop.setDate(backend.string_to_date(self.settings_pack["date_stop"]))
        else:
            self.calendar_start.setDate(QDate.currentDate().addYears(-1))
            self.calendar_stop.setDate(QDate.currentDate())

        for interval in list(self.interval_list):
            self.interval.addItem(interval)

        # self.interval.setCurrentText(self.settings_pack["intervals"])
        self.interval.setCurrentIndex(int(self.settings_pack["intervals"]))

        # list for methods
        self.method_list.sort()

        for method in self.method_list:
            self.methods.addItem(method)

        self.methods.setCurrentText(self.settings_pack["methods"])
        self.methods.setCurrentIndex(int(self.settings_pack["methods"]))

        self.top_plot_variables = {"title": self.title_top, "currencies": (self.currencies_top_list1, self.currencies_top_list2),
                               "dates": (self.calendar_start, self.calendar_stop), "interval": self.interval}

        self.bottom_plot_variables = {"title": self.title_bottom, "currencies": (self.currencies_bottom_list1, self.currencies_bottom_list2),
                               "dates": (self.calendar_start, self.calendar_stop), "interval": self.interval}

        self.currencies_bottom_list1.currentIndexChanged.connect(self.graph_preview_bottom_change)
        self.currencies_bottom_list2.currentIndexChanged.connect(self.graph_preview_bottom_change)

        self.currencies_top_list1.currentIndexChanged.connect(self.graph_preview_top_change)
        self.currencies_top_list2.currentIndexChanged.connect(self.graph_preview_top_change)

        self.interval.currentIndexChanged.connect(self.graph_preview_top_change)
        self.title_top.textChanged.connect(self.graph_preview_top_change)
        self.calendar_start.dateChanged.connect(self.graph_preview_top_change)
        self.calendar_stop.dateChanged.connect(self.graph_preview_top_change)

        self.interval.currentIndexChanged.connect(self.graph_preview_bottom_change)
        self.title_bottom.textChanged.connect(self.graph_preview_bottom_change)
        self.calendar_start.dateChanged.connect(self.graph_preview_bottom_change)
        self.calendar_stop.dateChanged.connect(self.graph_preview_bottom_change)

        self.graph_preview_top = backend_graph.create_plot(self.graph_preview_top, self.top_plot_variables)
        self.graph_preview_bottom = backend_graph.create_plot(self.graph_preview_bottom, self.bottom_plot_variables)

        self.title_top.setPlaceholderText(self.currencies_top_list1.currentText()[:3]
        + '/' + self.currencies_top_list2.currentText()[:3])

        self.title_bottom.setPlaceholderText(self.currencies_bottom_list1.currentText()[:3]
        + '/' + self.currencies_bottom_list2.currentText()[:3])

        # main tab layout
        self.tab_main.layout = QGridLayout()  # 2. layout
        self.tab_main.layout.setSpacing(10)

        self.tab_main.layout.setContentsMargins(0, 0, 0, 0)

        # Ustawic to jako tab
        self.tab_main.layout.addWidget(self.button_settings, 0, 2, alignment = Qt.AlignRight)

        self.tab_main.layout.addWidget(self.title_top, 1, 2, alignment=Qt.AlignLeft)
        self.tab_main.layout.addWidget(self.title_bottom, 1, 2, alignment=Qt.AlignRight)

        # currencies bottom layout
        self.tab_main.layout.addWidget(self.currencies_bottom_label, 3, 0, 1, 2, alignment=Qt.AlignHCenter)
        self.tab_main.layout.addWidget(self.currencies_bottom_list1, 4, 0, 1, 1, alignment=Qt.AlignHCenter)
        self.tab_main.layout.addWidget(self.currencies_bottom_list2, 5, 0, 1, 1, alignment=Qt.AlignHCenter)
        self.tab_main.layout.addWidget(self.swap_currencies_bottom, 4, 1, 2, 1, alignment=Qt.AlignHCenter)

        # currencies top layout
        self.tab_main.layout.addWidget(self.currencies_top_label, 0, 0, 1, 2, alignment=Qt.AlignHCenter)
        self.tab_main.layout.addWidget(self.currencies_top_list1, 1, 0, 1, 1 , alignment=Qt.AlignHCenter)
        self.tab_main.layout.addWidget(self.currencies_top_list2, 2, 0, 1, 1 , alignment=Qt.AlignHCenter)
        self.tab_main.layout.addWidget(self.swap_currencies_top, 1, 1, 2, 1, alignment=Qt.AlignHCenter)

        # checkbox layout
        self.tab_main.layout.addWidget(self.checkbox, 3, 0, 1, 2, alignment=Qt.AlignLeft)

        self.tab_main.layout.addWidget(self.calendar_start_label, 6, 0, 1, 2, alignment=Qt.AlignHCenter)
        self.tab_main.layout.addWidget(self.calendar_start, 7, 0, 1, 2)
        self.tab_main.layout.addWidget(self.calendar_stop_label, 8, 0, 1, 2, alignment=Qt.AlignHCenter)
        self.tab_main.layout.addWidget(self.calendar_stop, 9, 0, 1, 2)
        self.tab_main.layout.addWidget(self.interval_label, 10, 0, 1, 2, alignment=Qt.AlignHCenter)
        self.tab_main.layout.addWidget(self.interval, 11, 0, 1, 2)
        self.tab_main.layout.addWidget(self.method_label, 12, 0, 1, 2, alignment=Qt.AlignHCenter)
        self.tab_main.layout.addWidget(self.methods, 13, 0, 1, 2)

        self.tab_main.layout.addWidget(self.button_plot, 14, 0, 1, 2, alignment=Qt.AlignHCenter)

        self.tab_main.layout.addWidget(self.graph_preview_top, 2, 2, 6, 1)
        self.tab_main.layout.addWidget(self.graph_preview_bottom, 8, 2, 7, 1)

        self.tab_main.setStyleSheet(mainTabStyleSheet)

        self.layout.addWidget(self.tabs)
        self.tab_main.setLayout(self.tab_main.layout)

        ll = QWidget()
        ll.setLayout(self.layout)
        self.setCentralWidget(ll)

    def graph_preview_top_change(self):
        self.graph_preview_top = backend_graph.create_plot(self.graph_preview_top, self.top_plot_variables)

    def graph_preview_bottom_change(self):
        self.graph_preview_bottom = backend_graph.create_plot(self.graph_preview_bottom, self.bottom_plot_variables)

    def swap_currencies(self):
        tmp = self.currencies_bottom_list1.currentText()
        self.currencies_bottom_list1.setCurrentText(self.currencies_bottom_list2.currentText())
        self.currencies_bottom_list2.setCurrentText(tmp)

    def swap_currencies2(self):
        tmp = self.currencies_top_list1.currentText()
        self.currencies_top_list1.setCurrentText(self.currencies_top_list2.currentText())
        self.currencies_top_list2.setCurrentText(tmp)

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
                                                   self.save_settings_to_file, self.reset_settings, self.checkbox)
        self.settings_pack = p

        self.tabs.addTab(tab, "Ustawienia")
        self.tabs.setCurrentIndex(self.tabs.indexOf(tab))

        self.settings_tab = tab

    def help(self):
        help_file = os.getcwd() + "/help/index.html"
        print(help_file)
        webbrowser.open("file:///" + help_file)
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

        self.currencies_bottom_list1.setCurrentIndex(self.settings_pack["currencies12"].currentIndex())
        self.currencies_bottom_list2.setCurrentIndex(self.settings_pack["currencies21"].currentIndex())
        self.currencies_top_list1.setCurrentIndex(self.settings_pack["currencies1"].currentIndex())
        self.currencies_top_list2.setCurrentIndex(self.settings_pack["currencies2"].currentIndex())
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
        currency12 = "currency12:" + str(self.settings_pack["currencies12"].currentIndex()) + '\n'
        currency21 = "currency21:" + str(self.settings_pack["currencies21"].currentIndex()) + '\n'
        method = "method:" + str(self.settings_pack["methods"].currentIndex()) + '\n'
        interval = "interval:" + str(self.settings_pack["intervals"].currentIndex()) + '\n'

        date_start = "date_start:" + backend.return_date(self.settings_pack["date_start"]) + '\n'
        date_stop = "date_stop:" + backend.return_date(self.settings_pack["date_stop"]) + '\n'
        checkbox = "checkbox:" + str(self.settings_pack["date_checkbox"].isChecked()) + '\n'
        settings = [currency1, currency2, method, interval, date_start, date_stop, checkbox,
         currency12, currency21]
        open('settings', 'w').writelines(settings)

    def read_settings_from_file(self):
        f = open('settings', "r").readlines()
        settings = []
        for line in f:
            settings.append(line.split(':')[1][:-1])

        self.settings_pack = {"currencies1": settings[0], "currencies2": settings[1],
                              "methods": settings[2], "intervals": settings[3], "date_start": settings[4],
                              "date_stop": settings[5], "date_checkbox": settings[6],
                              "currencies12": settings[7], "currencies21": settings[8]}

    def reset_settings(self):
        f = open('default_settings', "r").readlines()
        settings = []
        for line in f:
            settings.append(line.split(':')[1][:-1])

        self.settings_pack = {"currencies1": settings[0], "currencies2": settings[1],
                              "methods": settings[2], "intervals": settings[3], "date_start": settings[4],
                              "date_stop": settings[5], "date_checkbox": settings[6],
                              "currencies12": settings[7], "currencies21": settings[8]}

        currency1 = "currency1:" + self.settings_pack["currencies1"] + '\n'
        currency2 = "currency2:" + self.settings_pack["currencies2"] + '\n'
        currency12 = "currency12:" + self.settings_pack["currencies12"] + '\n'
        currency21 = "currency21:" + self.settings_pack["currencies21"] + '\n'
        method = "method:" + self.settings_pack["methods"] + '\n'
        interval = "interval:" + self.settings_pack["intervals"] + '\n'
        date_start = "date_start:" + self.settings_pack["date_start"] + '\n'
        date_stop = "date_stop:" + self.settings_pack["date_stop"] + '\n'
        checkbox = "checkbox:" + self.settings_pack["date_checkbox"] + '\n'
        settings_new = [currency1, currency2, method, interval, date_start, date_stop, checkbox,
        currency12, currency21]
        open('settings', 'w').writelines(settings_new)

        self.close_tab(False)
        self.settings()

    # load csv (with anomaly column)
    def graph_from_file(self):
        file, _ = QFileDialog.getOpenFileName(self, "Detektor anomalii", "", "CSV Files (*.csv *.txt)",
                                              options=QFileDialog.Options())
        if file is None or file == "": return

        csv_list, error = backend.download_csv([file])

        if error == "empty":
            backend.error("Błedny plik", "Wprowadzony plik jest pusty lub posiada zbyt mało danych")

        if csv_list is None or any(csv is None for csv in csv_list): return

        pack = {"method": "", "csv": csv_list[0], "title": "Wykres " + file.split('/')[-1], "date": "Date",
                "target": "Exchange"}

        self.pack_data(pack)

    # load csv (without anomaly column)
    def file_open(self):
        file, _ = QFileDialog.getOpenFileName(self, "Detektor anomalii", "", "CSV Files (*.csv *.txt)",
                                              options=QFileDialog.Options())
        if file is None or file == "": return

        tab, pack = backend_funcs.create_graph_tab(close=self.close_tab, pack_fun=self.pack_data, file=file,
                                                   methods_list=self.method_list, important=self.important_add_tab)

        if tab is None or pack is None: return

        self.pack[tab] = pack
        self.tabs.addTab(tab, file.split('/')[-1])
        self.tabs.setCurrentIndex(self.tabs.indexOf(tab))

    # load csv (used while loading data without anomaly as an trigger to button named "Wygeneruj wykres")
    def pack_data(self, pack):
        from_file = True
        errors = ""

        if pack is False:   # load without anomaly ("Otwórz")
            pack = self.pack[self.tabs.currentWidget()]
            from_file = False
            method = pack["method"].currentText()
            title = pack["title"].text()
            date = pack["date"].currentText()
            target = [elem.currentText() for elem in pack["target"]]
            if 'Nie wybrano' in target: target.pop()
            elif target[0] == target[1]: backend.error("Wybrano te same kolumny"); return
            csv = pack["csv"]
            date_format = pack["format1"].currentText() + '-' + pack["format2"].currentText() + '-' + pack[
                "format3"].currentText()

            for row in csv[date]:
                if not isinstance(row, str): errors += "Błędne dane w kolumnie " + date + ", dane muszą być w formie textu" + "\n"; break
            for t in target:
                for row in csv[t]:
                    if not isinstance(row, float): errors += "Błędne dane w kolumnie " + t + ", dane muszą być liczbą rzeczywistą" + "\n"; break
            if errors != "": backend.error(errors); return
            elif backend.check_date(csv, date, date_format) is None: return

        else:   # load with anomaly ("Otwórz graf")
            method = pack["method"]
            title = pack["title"]
            date = pack["date"]
            target = pack["target"]
            csv = pack["csv"]

            columns = csv.columns.tolist()  # get list of columns in csv file

            if from_file and not len([name for name in columns if 'Anomaly' in name]):  # for graph_from_file() Anomaly is mandatory
                backend.error("Nie znaleziono informacji o anomaliach")
                return

            current_columns_names = None
            for key, value in expected_columns.items():
                if columns == value:
                    current_columns_names = key     # get suit key, based on values
                    break

            if current_columns_names in ['single_with_anomaly_all', 'multiple_with_anomaly_all']:
                method = 'Wszystkie'    # needed in graph_init, no info about that from csv

            if current_columns_names is not None:
                for col in columns:
                    if 'Date' in col and backend.check_date(csv, col, 'Rok-Miesiąc-Dzień') is None: return
                    elif 'Exchange' in col:
                        for row in csv[col]:
                            if not isinstance(row, float): errors += "Błędne dane w kolumnie " + col + ", dane muszą być liczbą rzeczywistą" + "\n"; break
                    elif 'Anomaly' in col:
                        for row in csv[col]:
                            if not isinstance(row, bool): errors += "Błędne dane w kolumnie " + col + ", dane muszą być wartościami True lub False" + "\n"; break
                if errors != "": backend.error(errors); return
            else:
                for key, value in expected_columns.items(): errors += str(key) + " -> " + str(value) + "\n"
                backend.error("Niepoprawne nazwy kolumn, możliwe formaty: \n" + errors)
                return

        self.create_graph(csv_list=[csv], method=method, date=date, target=target, title=title,
                          with_anomalies=from_file)

    # download csv
    def download_data(self):
        pressed = backend.error("Czy chcesz również pobrać dane o anomaliach?", icon=QMessageBox.Question,
                                buttons=QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel, title="Dane")

        if pressed != QMessageBox.Cancel:
            graphs = self.graphs[self.tabs.currentWidget()] # get graphs from current tab
            datas = [graph.anomalies_to_download[graph.data_indexes[0]:graph.data_indexes[1]] for graph in graphs]  # get datas

            if pressed == QMessageBox.No:   # if we want to download only data (without anomaly)
                for i in range(len(datas)):
                    if graphs[i].method == "Wszystkie":
                        for anomalies in graphs[i].anomalies_list:
                            datas[i] = datas[i].drop(anomalies, axis=1)     # dropping columns with anomaly
                    else: datas[i] = datas[i].drop("Anomaly", axis=1)

            file, _ = QFileDialog.getSaveFileName(self, "Detektor anomalii", "anomaly detection data",
                                                  "CSV Files (*.csv);;Text Files(*.txt)", options=QFileDialog.Options())
            if file == "" or any(data is None for data in datas): return

            # decide what kind of data should we download, based on number of graphs from currentWidget (not by checkbox.isClicked)
            if len(self.graphs[self.tabs.currentWidget()]) > 1:
                merged = pd.DataFrame()
                for i in range(len(datas)): # go through list of dataframes and add index to every column name
                    col_list = datas[i].columns.values.tolist() # get list of column names
                    for j in range(len(col_list)):
                        datas[i].rename(columns={col_list[j] : col_list[j] + '-' + str(i+1)}, inplace=True) # add index to column name
                    merged = pd.concat([merged, datas[i]], axis=1)  # append single dataframe to merged dataframe
                # delete one of Date columns (same data, so can be deleted)
                merged = merged.drop('Date-2', axis=1)
                merged.rename(columns={'Date-1' : 'Date'}, inplace=True)
            else: merged = datas[0]

            try:
                merged.to_csv(file, index=False)
            except PermissionError:
                backend.error("Brak dostępu do lokalizacji pliku", "Sprawdź czy plik jest zamknięty jeśli istnieje.")
        else: return

    # download img
    def download_graph(self):
        # TODO: concatenate 2 plots into 1 img
        graphs = self.graphs[self.tabs.currentWidget()]

        exporter_list = []
        for i in range(len(graphs)):
            plt = graphs[i].graph
            exporter_list.append(exporters.ImageExporter(plt.plotItem))
            exporter_list[i].parameters()['width'] = 1920

        file, _ = QFileDialog.getSaveFileName(self, "Detektor anomalii", "anomaly detection plot",
                                              "PNG Files (*.png);;JPEG Files(*.jpg)", options=QFileDialog.Options())

        if file == "": return
        filepath, extension = file.split(".")   # will carsh if file path will contain more dots

        try:
            # decide what kind of data should we download, based on number of graphs from currentWidget (not by checkbox.isClicked)
            if len(self.graphs[self.tabs.currentWidget()]) > 1:
                for i in range(len(exporter_list)): exporter_list[i].export(filepath + '_' + str(i+1) + '.' + extension)
            else: exporter_list[0].export(file)
        except PermissionError:
            backend.error("Brak dostępu do lokalizacji pliku", "Sprawdź czy plik jest zamknięty jeśli istnieje.")

    def create_plot(self):
        date = "Data"
        target = "Zamkniecie"

        date_start = backend.return_date(self.calendar_start)
        date_stop = backend.return_date(self.calendar_stop)
        interval = self.interval.currentText()
        method = self.methods.currentText()
        currencies = list()
        currencies.append(self.currencies_bottom_list1.currentText()[:3])
        currencies.append(self.currencies_bottom_list2.currentText()[:3])
        if self.checkbox.isChecked():
            currencies.append(self.currencies_top_list1.currentText()[:3])
            currencies.append(self.currencies_top_list2.currentText()[:3])
        title = self.title_top.text()
        if title == "":
            title = currencies[0] + "/" + currencies[1] # temporary

        links = backend.create_link(currencies, date_start, date_stop, interval)
        csv_list, error = backend.download_csv(links)

        if error == "connection error":
            return

        if csv_list is None:
            backend.input_errors(currencies, self.calendar_start.date(), self.calendar_stop.date())
        else:
            self.create_graph(csv_list=csv_list, method=method, date=date, target=target, title=title, currencies=currencies)
            if self.checkbox.isChecked():
                self.differential = True
                self.create_graph(csv_list=csv_list, method=method, date=date, target=target, title=title+" Różnicowa", currencies=currencies)

    def create_graph(self, csv_list, method, date, target, title="", currencies=None, with_anomalies=False):
        if currencies is None: currencies = [None for _ in range(4)] # legacy
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

        new_graphs = list()

        new_csv_list = split_csv(csv_list[0], rename=with_anomalies)   # try to split csv
        if new_csv_list: csv_list = new_csv_list    # if splitting was success, override cev_list

        # if Exchange_2 and _1 are taken, but split_csv() always split in order, so might happened _2 != _1 and _1 != _2
        if isinstance(target, list) and target[0] not in csv_list[0].columns.tolist():
            csv_list.reverse()  # reorder

        # in case if user want to generate 1 plot from csv that can generate 2 plots
        if isinstance(target, list) and len(target) == 1 and len(csv_list) > 1:
            if target[0] not in csv_list[0].columns.tolist():
                csv_list.pop(0)
            elif target[0] not in csv_list[1].columns.tolist():
                csv_list.pop(1)

        if self.differential:
            csv_list = differential_analysis.get_anomalies(csv_list, target, method, date)
            self.differential = False
            target = 'Exchange'
            date = 'Date'
            with_anomalies = True

        new_graphs.append(Graph(method=method, csv=csv_list[0], date=date, target=target if not isinstance(target, list) else target[0], currency1=currencies[0], currency2=currencies[1],
                          label=label, slider=slider, slider_label=slider_label,
                          checkbox=refresh_checkbox, date_label=date_label, value_label=value_label, title=title,
                          with_anomalies=with_anomalies))
        # tab.layout.addWidget(new_graphs[0].graph, alignment=Qt.Alignment())

        if len(csv_list) > 1:
            new_graphs.append(Graph(method=method, csv=csv_list[1], date=date, target=target if not isinstance(target, list) else target[1], currency1=currencies[2],
                               currency2=currencies[3],
                               label=label, slider=slider, slider_label=slider_label,
                               checkbox=refresh_checkbox, date_label=date_label, value_label=value_label, title=title,
                               with_anomalies=with_anomalies))
            tab.layout.addWidget(new_graphs[1].graph, alignment=Qt.Alignment())

            tab.layout.addWidget(new_graphs[0].graph, alignment=Qt.Alignment())

            if new_graphs[0].currency1 != "" and new_graphs[0].currency2 != "":
                new_graphs[0].title = new_graphs[0].currency1 + '/' + new_graphs[0].currency2
                new_graphs[0].graph.setTitle(new_graphs[0].title)
                new_graphs[0].refresh_graph()

            if new_graphs[1].currency1 != "" and new_graphs[1].currency2 != "":
                new_graphs[1].title = new_graphs[1].currency1 + '/' + new_graphs[1].currency2
                new_graphs[1].graph.setTitle(new_graphs[1].title)
                new_graphs[1].refresh_graph()

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
                button_reset.clicked.connect(new_graphs[0].reset_slider)
                tab.layout.addLayout(slider_layout)

        for i in range(len(new_graphs)):
            button_flip.clicked.connect(new_graphs[i].flip)
            slider.valueChanged.connect(new_graphs[i].update_graph)
            button_refresh.clicked.connect(new_graphs[i].refresh_graph)
            button_reset_graph.clicked.connect(new_graphs[i].reset_graph)
        tab.setLayout(tab.layout)

        self.graphs[tab] = new_graphs
        self.tabs.setCurrentIndex(self.tabs.indexOf(tab))

        self.differential = False


def split_csv(csv_to_split: pd.DataFrame, rename: bool) -> list:
    ''' Function that splits csv file on 2 dataframes
    if csv columns are one of the expected_columns containing word multiply (last 3 values) '''
    columns = csv_to_split.columns.tolist() # get columns names
    if columns in list(expected_columns.values())[3:]:  # only in case of 2 plots in one csv (last 3 values)
        cols_no = len(columns)
        splitted = list()
        splitted.append(csv_to_split.iloc[:, 0:cols_no // 2 + 1])   # split on a half
        splitted.append(csv_to_split.iloc[:, [0] + list(np.arange(cols_no // 2 + 1, cols_no, dtype=int))])  # get second half with Date column as first
        if rename:
            for sp in splitted:
                for col in sp.columns.tolist():
                    sp.rename(columns={col: col.split('-')[0]}, inplace=True)   # rename all columns by splitting by '-' (easiest way to connect with existing API)
        return splitted
    else: return []

def main():
    app = QApplication(sys.argv)
    ex = Window()
    ex.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
