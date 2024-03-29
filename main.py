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
from pyqtgraph import functions as fn
import pyqtgraph as pg
from PIL import Image


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
    """
        Function takes a layout as an input and removes all the widgets from that layout.
    """
    while layout.count():
        child = layout.takeAt(0)
        if child.widget():
            child.widget().deleteLater()


class Calendar(QCalendarWidget):
    """
        Custom QCalendarWidget that inherits from the Qt QCalendarWidget class. It is used to display a calendar widget in the GUI.
    """
    def __init__(self, parent=None):
        super(Calendar, self).__init__(parent)
        self.setGridVisible(True)
        self.setStyleSheet(calendarStyleSheet)


class Window(QMainWindow):
    """
        Subclass of QMainWindow that provides a graphical user interface for a tool that performs anomaly detection on financial data.

        Args:
            -differential: A boolean indicating whether the differential of the dataset is being displayed.
            -graph_preview_top: A pg.PlotWidget instance representing the top graph preview in the UI.
            -graph_preview_bottom: A pg.PlotWidget instance representing the bottom graph preview in the UI.
            -top_plot_variables: A dictionary of variables related to the top graph preview.
            -bottom_plot_variables: A dictionary of variables related to the bottom graph preview.
            -important_tabs: A list of tabs in the UI that should not be closed.
            -help_tab: A reference to the help tab in the UI.
            -settings_tab: A reference to the settings tab in the UI.
            -creators_tab: A reference to the creators tab in the UI.
            -button_settings: A QPushButton instance that opens the settings menu.
            -settings_pack: A dictionary containing settings loaded from a configuration file.
            -interval_list: A list of strings representing the possible intervals to display in the UI.
            -pack: A dictionary containing configuration settings for the current dataset.
            -tabs: A QTabWidget instance representing the tabbed interface for the UI.
            -tab_main: A QWidget instance representing the main tab in the UI.
            -graphs: A dictionary containing references to the various plots in the UI.
            -button_plot: A QPushButton instance that generates the plot.
            -swap_currencies_bottom: A QPushButton instance that swaps the currencies in the bottom graph.
            -swap_currencies_top: A QPushButton instance that swaps the currencies in the top graph.
            -calendar_start_label: A QLabel instance representing the label for the start date.
            -calendar_start: A QDateEdit instance representing the widget for selecting the start date.
            -calendar_stop_label: A QLabel instance representing the label for the end date.
            -calendar_stop: A QDateEdit instance representing the widget for selecting the end date.
            -method_list: A list of strings representing the possible anomaly detection methods to use.
            -method_label: A QLabel instance representing the label for the method selection.
            -methods: A QComboBox instance representing the drop-down for selecting the anomaly detection method.
            -interval_label: A QLabel instance representing the label for the interval selection.
            -interval: A QComboBox instance representing the drop-down for selecting the interval.
            -currencies_bottom_label: A QLabel instance representing the label for the currency selection in the bottom graph.
            -currencies_bottom_list1: A QComboBox instance representing the drop-down for selecting the first currency in the bottom graph.
            -currencies_bottom_list2: A QComboBox instance representing the drop-down for selecting the second currency in the bottom graph.
            -checkbox: A QCheckBox instance representing the checkbox for disabling a currency in the bottom graph.
            -currencies_top_label: A QLabel instance representing the label for the currency selection in the top graph.
            -currencies_top_list1: A QComboBox instance representing the drop-down for selecting the first currency in the top
    """
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
        """
            Method is called when the currency is changed in the top plot.
            It sets the placeholder text of the top plot title line edit widget to the text of the top plot.
        """
        self.title_top.setPlaceholderText(
            #self.graph_preview_top.text() #to moze dobrze
        )


    def change_label_bottom(self): # zmienic funkcje nie dziala w kazdym przypadku
        """
            function is used to set the text of the placeholder in the QLineEdit widget for the title of the bottom plot
        """
        self.title_bottom.setPlaceholderText(
            # self.bottom_plot_variables["currencies"][0].currentText()[:3] + '/' +
            # self.bottom_plot_variables["currencies"][1].currentText()[:3]
            #self.graph_preview_bottom.text() #to moze dobrze
        )


    def swap_clicked_top(self):
        """
            function handles a click event for the swap currencies button in the top graph.
            When the button is clicked, it swaps the currencies selected in the top graph's currency selection comboboxes and updates the title placeholder text accordingly.
            If the current placeholder text in the title matches the current currency selection, it updates the placeholder text to show the new currency selection in reverse order.
            Otherwise, it updates the placeholder text to show the currency selection in the original order.
        """
        if self.title_top.placeholderText() == self.currencies_top_list1.currentText()[:3] + '/' + self.currencies_top_list2.currentText()[:3]:
            self.title_top.setPlaceholderText(
                self.currencies_top_list2.currentText()[:3] + '/' + self.currencies_top_list1.currentText()[:3]
            )
        else:
             self.title_top.setPlaceholderText(
                self.currencies_top_list1.currentText()[:3] + '/' + self.currencies_top_list2.currentText()[:3]
            )


    def swap_clicked_bottom(self):
        """
            function swaps the currencies shown in the graph title and updates the title.
            It checks if the current title matches the format 'currency1/currency2' and if it does, it swaps the currency abbreviations and updates the title.
            If it does not match this format, it sets the title to 'currency1/currency2
        """
        if self.title_bottom.placeholderText() == self.currencies_bottom_list1.currentText()[:3] + '/' + self.currencies_bottom_list2.currentText()[:3]:
            self.title_bottom.setPlaceholderText(
                self.currencies_bottom_list2.currentText()[:3] + '/' + self.currencies_bottom_list1.currentText()[:3]
            )
        else:
             self.title_bottom.setPlaceholderText(
                self.currencies_bottom_list1.currentText()[:3] + '/' + self.currencies_bottom_list2.currentText()[:3]
            )


    def checkbox_clicked(self):
        """
            slot function that handles the state change of the checkbox.
            If the checkbox is checked, it enables the top plot along with its corresponding controls and updates the label of the checkbox to "Wyłącz".
            If the checkbox is unchecked, it disables the top plot and its corresponding controls and updates the label of the checkbox to "Włącz".
        """
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
        """
            menu bar with several menu items .
            Each menu item is connected to a specific function, which is triggered when the user selects the menu item.
        """
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
        """
            function initializes the main layout of the application. It creates several widgets and adds them to the layout using a QGridLayout.
            The layout includes widgets for selecting currencies, dates, intervals and methods, as well as a button to plot the graphs and a checkbox to enable/disable the second graph.
            It also initializes the graph preview widgets with default values and connects signals to slots to update the graph previews when the user changes any of the settings.
            Finally, it sets the main layout of the application to be the QGridLayout and sets it as the central widget.
        """
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
        """
            Swapping currencies.
        """
        tmp = self.currencies_bottom_list1.currentText()
        self.currencies_bottom_list1.setCurrentText(self.currencies_bottom_list2.currentText())
        self.currencies_bottom_list2.setCurrentText(tmp)

    def swap_currencies2(self):
        """
            Swaps the selected currencies in two dropdown menus.
        """
        tmp = self.currencies_top_list1.currentText()
        self.currencies_top_list1.setCurrentText(self.currencies_top_list2.currentText())
        self.currencies_top_list2.setCurrentText(tmp)

    def important_add_tab(self):
        """
            Adds or removes a tab from a list of "important" tabs, and sets or removes an icon to indicate whether the tab is important
        """
        tab = self.tabs.currentWidget()
        if tab not in self.important_tabs:
            self.tabs.setTabIcon(self.tabs.indexOf(tab), QIcon(important_icon))
            self.important_tabs.append(tab)
        else:
            self.tabs.setTabIcon(self.tabs.indexOf(tab), QIcon(not_important_icon))
            self.important_tabs.pop(self.important_tabs.index(tab))

    def close_tab(self, index):
        """
            Args:
                -index (int or bool): The index of the tab to be closed, or a boolean value indicating that the currently selected tab should be closed.

                Close the tab in QTabWidget.
        """
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
        """
            Function creating and displaying settings widget. When it already exists it switches to it.
        """
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
        """
            Creators of project
        """
        if self.creators_tab is not None:
            self.tabs.setCurrentIndex(self.tabs.indexOf(self.creators_tab))
            return

        tab = backend_funcs.create_creators_tab(self.close_tab)

        self.tabs.addTab(tab, "Twórcy")
        self.tabs.setCurrentIndex(self.tabs.indexOf(tab))

        self.creators_tab = tab

    def save_settings_to_file(self):
        """
            Saves the user's settings to a file named "settings". The method sets various UI elements to the values in the settings_pack dictionary.
        """
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
        """
            Reads the user's settings from a file named "settings" and populates the settings_pack dictionary with the values.
        """
        f = open('settings', "r").readlines()
        settings = []
        for line in f:
            settings.append(line.split(':')[1][:-1])

        self.settings_pack = {"currencies1": settings[0], "currencies2": settings[1],
                              "methods": settings[2], "intervals": settings[3], "date_start": settings[4],
                              "date_stop": settings[5], "date_checkbox": settings[6],
                              "currencies12": settings[7], "currencies21": settings[8]}

    def reset_settings(self):
        """
            Resets the user's settings to their default values by reading the "default_settings" file and overwriting the "settings" file with the default values.
            The method then closes the current tab and opens the settings tab to show the new settings.
        """
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
        """
            Allows the user to select a CSV file using a file dialog, which is then used to create a graph.
            The method first displays a file dialog using the `getOpenFileName()` method of the `QFileDialog` class, which allows the user to select a CSV file.
            If the user selects a file, the `download_csv()` function from the `backend` module is called with a list containing the selected file.
            The `download_csv()` function reads the CSV file and returns a list containing a `pandas` DataFrame for each CSV file.
            The method then checks for any errors and displays an error message if necessary.
            If there are no errors, the method creates a dictionary `pack` with keys for the graph method, the CSV data, the title of the graph, the x-axis label, and the y-axis label.
            The `pack_data()` method is then called with the `pack` dictionary to create a graph from the CSV data.
        """
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
        """
            Allows the user to select a CSV file using a file dialog and create a graph from the data in the selected file.
            The method first displays a file dialog using the `getOpenFileName()` method of the `QFileDialog` class, which allows the user to select a CSV file.
            If the user selects a file, the `create_graph_tab()` function from the `backend_funcs` module is called with the selected file, a list of available graph methods, and several callback functions.
            The `create_graph_tab()` function reads the CSV file and creates a tab containing a graph and controls for the user to adjust the graph settings.
            The `create_graph_tab()` function returns a tuple containing the graph tab and a dictionary containing the graph data and settings.
            If there are errors creating the graph tab or dictionary, the method returns early. If the graph tab and dictionary are successfully created, the method adds the graph tab to the
            `QTabWidget` object and sets the current tab to the new graph tab.
        """
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
        """
            Create graph from provided data. Load graph with or without anomalies. If the pack is false create graph without anomalies.
            If data is incomplete or has ane errors error message is showed.
        """
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

            if csv.isnull().values.any():   # in case of incomplete data
                backend.error('Dane zawierają wartości nieokreślone: nan')
                return

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

            if csv.isnull().values.any():   # in case of incomplete data
                backend.error('Dane zawierają wartości nieokreślone: nan')
                return

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
        """
            Downloading data from current opened graph. Ask user if he wants to downlaod anomaly data.
        """
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
        """
            User can download graph as PNG or JPEG file.
        """
        graphs = self.graphs[self.tabs.currentWidget()]

        exporter_list = []
        array_list = []
        for i in range(len(graphs)):
            plt = graphs[i].graph
            exporter_list.append(exporters.ImageExporter(plt.plotItem))
            exporter_list[i].parameters()['width'] = 1920
            array_list.append(fn.ndarray_from_qimage(exporter_list[i].export(toBytes=True)))

        file, _ = QFileDialog.getSaveFileName(self, "Detektor anomalii", "anomaly detection plot",
                                              "PNG Files (*.png);;JPEG Files(*.jpg)", options=QFileDialog.Options())

        if file == "": return

        try:
            if len(self.graphs[self.tabs.currentWidget()]) > 1:
                output_img = np.concatenate((array_list[0], array_list[1]), axis=0)
            else: output_img = array_list[0]

            extension = file.split('.')[-1]
            if extension == 'jpg':
                output_img = output_img[:, :, :-1]  # cut alpha channel
                output_img = output_img[:, :, ::-1] # swap from BGR to RGB for .jpg
            elif extension == 'png':
                output_img[:, :, [0, 2]] = output_img[:, :, [2, 0]]  # swap from BGRA to RGBA for .png
            i = Image.fromarray(output_img)
            i.save(file)
        except PermissionError:
            backend.error("Brak dostępu do lokalizacji pliku", "Sprawdź czy plik jest zamknięty jeśli istnieje.")
        except Exception:
            backend.error("Unhandled exception")

    def create_plot(self):
        """
            Create new graph with data from user settings.
        """
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
        title_top = self.title_top.text()
        title_bottom = self.title_bottom.text()
        if title_top == "": title_top = currencies[0] + "/" + currencies[1]
        if self.checkbox.isChecked() and title_bottom == "": title_bottom = currencies[2] + "/" + currencies[3]

        links = backend.create_link(currencies, date_start, date_stop, interval)
        csv_list, error = backend.download_csv(links)

        # in case of different number rows or cols, just return error, there is no reason for differential analysis
        if len(csv_list) > 1 and csv_list[0].shape != csv_list[1].shape:
            backend.error('Dane nie posiadają tej samej ilości wierszy lub kolumn')
            return

        if error == "connection error":
            return

        if csv_list is None:
            backend.input_errors(currencies, self.calendar_start.date(), self.calendar_stop.date())
        else:
            self.create_graph(csv_list=csv_list, method=method, date=date, target=target, title=[title_top, title_bottom], currencies=currencies)
            if self.checkbox.isChecked():
                self.differential = True
                self.create_graph(csv_list=csv_list, method=method, date=date, target=target, title=[title_top + ' - Analiza różnicowa', title_bottom + ' - Analiza różnicowa'], currencies=currencies)

    def create_graph(self, csv_list, method, date, target, title=None, currencies=None, with_anomalies=False):
        """
            Creating new tab with graph based on provided data.
            If 'with_anomalies' is true, graph will include anommalies.

            Args:
                -csv_list: a list of pandas DataFrames containing the data to be plotted.
                -method: a string representing the anomaly detection method to use.
                -date: a string representing the name of the column in the data containing dates.
                -target: a string or list of strings representing the names of the columns in the data containing the target variables to be plotted.
                -title: an optional string representing the title of the graph.
                -currencies: an optional list of strings representing the currencies used in the data, used to set the title of the graph.
                -with_anomalies: a boolean indicating whether the graph should include anomalies.
        """
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
            self.tabs.addTab(tab, title[1] if isinstance(title, list) else title)
        else:
            if len(csv_list) > 1:
                new_title = title[1].split('-')
                if len(new_title) > 1: self.tabs.addTab(tab, method + new_title[1] if isinstance(title, list) else title)
                else: self.tabs.addTab(tab, method if isinstance(title, list) else title)
            else: self.tabs.addTab(tab, method + " " + title[1] if isinstance(title, list) else title)

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
                          checkbox=refresh_checkbox, date_label=date_label, value_label=value_label, title=title[1] if isinstance(title, list) else title,
                          with_anomalies=with_anomalies))
        if len(csv_list) == 1: tab.layout.addWidget(new_graphs[0].graph, alignment=Qt.Alignment())

        if len(csv_list) > 1:
            new_graphs.append(Graph(method=method, csv=csv_list[1], date=date, target=target if not isinstance(target, list) else target[1], currency1=currencies[2],
                               currency2=currencies[3],
                               label=label, slider=slider, slider_label=slider_label,
                               checkbox=refresh_checkbox, date_label=date_label, value_label=value_label, title=title[0] if isinstance(title, list) else title,
                               with_anomalies=with_anomalies))
            tab.layout.addWidget(new_graphs[1].graph, alignment=Qt.Alignment())

            tab.layout.addWidget(new_graphs[0].graph, alignment=Qt.Alignment())



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
