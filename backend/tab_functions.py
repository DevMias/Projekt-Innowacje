from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QIcon
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QLineEdit, QHBoxLayout, QComboBox, QDateEdit, \
    QCheckBox, QGridLayout

import main
from backend import backend_functions as backend
from front.styles import buttonStyleSheet, labelStyleSheet, comboBoxStyleSheet, currencies_list, DateEditStyleSheet, \
    flag_list, labelStyleSheet_big, labelStyleSheet_not_bold, important_icon, close_icon, comboBoxDisabledStyleSheet
from main import Calendar


def create_graph_tab(close, pack_fun, methods_list, file, important):
    """
                Args:
                    close: a function to close the tab
                    pack_fun: a function to pack the necessary parameters for the graph
                    methods_list: a list of available graphing methods
                    file: the file to be graphed
                    important: a function to mark the graph as important
                Functionality:
                    -Importing csv data using fucntion from backend_functions.py
                        Return: None if file is empty or has error
                    -QWidget object creating box layout
                    -QLineEdit object for the graph title adding it to the widget layout
                    -QComboBox object for the date format adding it to to the widget layout
                    -Function GenerateGraph button for widget layout, creating dictionary pack (nescessary elements for generating a graph)
                    -Pack:
                        -method: the QComboBox object for the graphing method
                        -csv: the Pandas DataFrame object of the CSV data
                        -title: the QLineEdit object for the graph title
                        -date: the QComboBox object for the date column
                        -target: a list of two QComboBox objects for the target column
                        -format1: the QComboBox object for the first date format
                        -format2: the QComboBox object for the second date format
                        -format3: the QComboBox object for the third date format
            """
    csv_data, error1 = backend.download_csv([file], from_file=True) # pass file as an list (required in this function)
    if csv_data is None: return None, None

    if error1 == "empty":
        backend.error("Błedny plik", "Wprowadzony plik jest pusty lub posiada zbyt mało danych")

    if any(csv is None for csv in csv_data):
        return None, None

    columns = csv_data[0].columns.tolist()  # one element list (csv_data), generated by download_csv function

    tab = QWidget()
    tab.layout = QVBoxLayout()
    horizontal_layout = QHBoxLayout()

    title_label = QLabel("Tytuł wykresu")
    title_label.setStyleSheet(labelStyleSheet)
    horizontal_layout.addWidget(title_label, alignment=Qt.Alignment())

    button_important = create_button(style=buttonStyleSheet, icon=QIcon(important_icon), function=important,
                                     max_size=(40, 40))
    horizontal_layout.addWidget(button_important, alignment=Qt.Alignment())

    button_close = create_button(style=buttonStyleSheet, icon=QIcon(close_icon), function=close, max_size=(40, 40))
    horizontal_layout.addWidget(button_close, alignment=Qt.Alignment())

    tab.layout.addLayout(horizontal_layout)

    title = QLineEdit()
    title.setStyleSheet(labelStyleSheet)
    title.setText(file.split('/')[-1][:-4])
    tab.layout.addWidget(title, alignment=Qt.Alignment())

    date_label = QLabel("Format daty")
    date_label.setStyleSheet(labelStyleSheet)

    date_layout = QHBoxLayout()

    date_format_box1 = QComboBox()
    date_format_box1.setStyleSheet(comboBoxStyleSheet)
    date_format_box2 = QComboBox()
    date_format_box2.setStyleSheet(comboBoxStyleSheet)
    date_format_box3 = QComboBox()
    date_format_box3.setStyleSheet(comboBoxStyleSheet)

    date_format_list = ["Dzień", "Miesiąc", "Rok"]

    for date_format in date_format_list:
        date_format_box1.addItem(date_format)
        date_format_box2.addItem(date_format)
        date_format_box3.addItem(date_format)

    date_format_box1.setCurrentText("Rok")
    date_format_box2.setCurrentText("Miesiąc")
    date_format_box3.setCurrentText("Dzień")

    date_label1 = QLabel(" ")
    date_label1.setStyleSheet(labelStyleSheet)

    date_layout.addWidget(date_format_box1, alignment=Qt.Alignment())
    date_layout.addWidget(date_format_box2, alignment=Qt.Alignment())
    date_layout.addWidget(date_format_box3, alignment=Qt.Alignment())
    date_layout.addWidget(date_label1, alignment=Qt.Alignment())
    date_layout.addWidget(date_label1, alignment=Qt.Alignment())
    date_layout.addWidget(date_label1, alignment=Qt.Alignment())

    tab.layout.addWidget(date_label, alignment=Qt.Alignment())
    tab.layout.addLayout(date_layout)

    date_column_label = QLabel("Kolumna z datą")
    date_column_label.setStyleSheet(labelStyleSheet)
    tab.layout.addWidget(date_column_label, alignment=Qt.Alignment())

    date_column = QComboBox()
    date_column.setStyleSheet(comboBoxStyleSheet)

    for column in columns:
        date_column.addItem(column)

    date_column.setCurrentText("Date")
    tab.layout.addWidget(date_column, alignment=Qt.Alignment())

    target_column_label = QLabel("Kolumna z wartością")
    target_column_label.setStyleSheet(labelStyleSheet)
    tab.layout.addWidget(target_column_label, alignment=Qt.Alignment())

    target_column_1, target_column_2 = QComboBox(), QComboBox()
    target_column_1.setStyleSheet(comboBoxStyleSheet)
    target_column_2.setStyleSheet(comboBoxStyleSheet)

    target_column_2.addItem('Nie wybrano')
    for column in columns:
        target_column_1.addItem(column)
        target_column_2.addItem(column)

    target_column_1.setCurrentText(columns[1])
    target_column_2.setCurrentText(columns[len(columns) // 2 + 1] if columns in list(main.expected_columns.values())[3:] else 'Nie wybrano')
    tab.layout.addWidget(target_column_1, alignment=Qt.Alignment())
    tab.layout.addWidget(target_column_2, alignment=Qt.Alignment())

    method_label = QLabel("Metoda")
    method_label.setStyleSheet(labelStyleSheet)

    methods = QComboBox()
    methods.setStyleSheet(comboBoxStyleSheet)

    for method in methods_list:
        methods.addItem(method)

    methods.setCurrentText("Większościowa")

    tab.layout.addWidget(method_label, alignment=Qt.Alignment())
    tab.layout.addWidget(methods, alignment=Qt.Alignment())

    button_plot = create_button(style=buttonStyleSheet, text="Wygeneruj wykres", function=pack_fun)

    tab.layout.addWidget(button_plot, alignment=Qt.Alignment())
    tab.setLayout(tab.layout)

    # pass first element of csv_data_list
    pack = {"method": methods, "csv": csv_data[0], "title": title, "date": date_column, "target": [target_column_1, target_column_2],
            "format1": date_format_box1, "format2": date_format_box2, "format3": date_format_box3}

    return tab, pack


def create_settings_tab(method_list, interval_list, close, save, reset, checkbox):
    """
                Args:
                    -method_list list of methods (strings) that are used in the application.
                    -interval_list list of intervals (strings) that are used in the application.
                    -close function that is called when the user clicks the "close" button on the tab.
                    -save function that is called when the user clicks the "save" button on the tab.
                    -reset function that is called when the user clicks the "reset" button on the tab.
                    -checkbox checkbox widget that is used to enable/disable certain functionalities.
                Functionality:
                    Reading current settings from a file setting values of the widgets.
                    User can modify settings and save them using "save" button and saving it in the file
                    Reset button to reset setting to default values
            """
    settings = read_settings_from_file()

    tab = QWidget()
    tab.layout = QVBoxLayout()

    # calendars for setting dates
    calendar_start_label = QLabel("Data początkowa")
    calendar_start_label.setStyleSheet(labelStyleSheet)
    calendar_stop_label = QLabel("Data końcowa")
    calendar_stop_label.setStyleSheet(labelStyleSheet)

    calendar_start = create_calendar(Calendar)
    calendar_stop = create_calendar(Calendar)

    calstart = QDateEdit()
    calstart.setStyleSheet(DateEditStyleSheet)
    calstart.setCalendarPopup(True)
    calstart.setDisplayFormat("dd-MM-yyyy")
    calstart.setCalendarWidget(calendar_start)
    calstart.setObjectName("settings_element")

    calstop = QDateEdit()
    calstop.setStyleSheet(DateEditStyleSheet)
    calstop.setCalendarPopup(True)
    calstop.setDisplayFormat("dd-MM-yyyy")
    calstop.setCalendarWidget(calendar_stop)
    calstop.setObjectName("settings_element")

    if settings["date_checkbox"] == "False":
        calstart.setDate(backend.string_to_date(settings["date_start"]))
        calstop.setDate(backend.string_to_date(settings["date_stop"]))
    else:
        calstart.setDate(QDate.currentDate().addYears(-1))
        calstop.setDate(QDate.currentDate())

    method_label = QLabel("Metoda")
    method_label.setStyleSheet(labelStyleSheet)
    methods = QComboBox()
    methods.setStyleSheet(comboBoxStyleSheet)
    methods.setObjectName("settings_element")

    # intervals
    interval_label = QLabel("Interwał")
    interval_label.setStyleSheet(labelStyleSheet)
    intervals = QComboBox()
    intervals.setStyleSheet(comboBoxStyleSheet)
    intervals.setObjectName("settings_element")

    # currencies
    currencies_top = QLabel("Waluty")
    currencies_top.setStyleSheet(labelStyleSheet)
    currencies_top_list1 = QComboBox()
    currencies_top_list1.setStyleSheet(comboBoxStyleSheet)
    currencies_top_list1.setObjectName("settings_element")
    currencies_top_list2 = QComboBox()
    currencies_top_list2.setStyleSheet(comboBoxStyleSheet)
    currencies_top_list2.setObjectName("settings_element")

    currencies_bottom_list1 = QComboBox()
    currencies_bottom_list1.setStyleSheet(comboBoxStyleSheet)
    currencies_bottom_list1.setObjectName("settings_element")
    currencies_bottom_list2 = QComboBox()
    currencies_bottom_list2.setStyleSheet(comboBoxStyleSheet)
    currencies_bottom_list2.setObjectName("settings_element")

    # lists for currencies
    for flag, currency in zip(flag_list, currencies_list):
        currencies_top_list1.addItem(QIcon(flag), currency)
        currencies_top_list2.addItem(QIcon(flag), currency)
        currencies_bottom_list1.addItem(QIcon(flag), currency)
        currencies_bottom_list2.addItem(QIcon(flag), currency)

    # currencies1.setCurrentText(settings["currencies1"])
    currencies_top_list1.setCurrentIndex(int(settings["currencies1"]))
    # currencies2.setCurrentText(settings["currencies2"])
    currencies_top_list2.setCurrentIndex(int(settings["currencies2"]))

    currencies_bottom_list1.setCurrentIndex(int(settings["currencies12"]))
    currencies_bottom_list2.setCurrentIndex(int(settings["currencies21"]))

    for interval in list(interval_list):
        intervals.addItem(interval)

    # intervals.setCurrentText(settings["intervals"])
    intervals.setCurrentIndex(int(settings["intervals"]))

    for method in method_list:
        methods.addItem(method)

    # methods.setCurrentText(settings["methods"])
    methods.setCurrentIndex(int(settings["methods"]))

    button_reset = create_button(style=buttonStyleSheet, text="Resetuj", function=reset, min_size=(150, 40))

    button_close = create_button(style=buttonStyleSheet, icon=QIcon(close_icon), function=close, max_size=(40, 40))

    default_label = QLabel("Ustawienia wartości domyślnych")
    default_label.setStyleSheet(labelStyleSheet)
    default_label.setObjectName("default_label")

    date_checkbox = QCheckBox()
    date_checkbox.setText("Ostatni rok")
    date_checkbox.setChecked(True)
    date_checkbox.setStyleSheet(buttonStyleSheet)
    date_checkbox.setObjectName("year_checkbox")

    button_save = create_button(style=buttonStyleSheet, text="Zapisz", function=save, min_size=(150, 40))
    button_save.setObjectName("settings_element")

    if checkbox.isChecked():
        currencies_top_list1.setEnabled(True)
        currencies_top_list2.setEnabled(True)
        currencies_top_list1.setStyleSheet(comboBoxStyleSheet)
        currencies_top_list2.setStyleSheet(comboBoxStyleSheet)
    else:
        currencies_top_list1.setEnabled(False)
        currencies_top_list2.setEnabled(False)
        currencies_top_list1.setStyleSheet(comboBoxDisabledStyleSheet)
        currencies_top_list2.setStyleSheet(comboBoxDisabledStyleSheet)

    tab.layout = QGridLayout()
    tab.layout.setSpacing(10)
    tab.layout.addWidget(default_label, 0, 1, 1, 2, alignment=Qt.AlignHCenter)
    tab.layout.addWidget(button_close, 0, 2, 1, 2, alignment=Qt.AlignRight)
    # self.tab_main.layout.addWidget(self.button_settings, 0, 2, alignment=Qt.AlignRight)

    tab.layout.addWidget(currencies_top, 2, 1, 1, 2, alignment=Qt.AlignHCenter)
    tab.layout.addWidget(currencies_top_list1, 3, 0, 1, 2, alignment=Qt.AlignLeft)
    tab.layout.addWidget(currencies_top_list2, 4, 0, 1, 2, alignment=Qt.AlignLeft)
    tab.layout.addWidget(currencies_bottom_list1, 3, 2, 1, 2, alignment=Qt.AlignRight)
    tab.layout.addWidget(currencies_bottom_list2, 4, 2, 1, 2, alignment=Qt.AlignRight)

    tab.layout.addWidget(calendar_start_label, 5, 1, 1, 2, alignment=Qt.AlignHCenter)
    tab.layout.addWidget(calstart, 6, 1, 1, 2, alignment=Qt.AlignHCenter)
    tab.layout.addWidget(calendar_stop_label, 7, 1, 1, 2, alignment=Qt.AlignHCenter)
    tab.layout.addWidget(calstop, 8, 1, 1, 2, alignment=Qt.AlignHCenter)
    tab.layout.addWidget(date_checkbox, 9, 1, 1, 2, alignment=Qt.AlignHCenter)

    tab.layout.addWidget(interval_label, 10, 1, 1, 2, alignment=Qt.AlignHCenter)
    tab.layout.addWidget(intervals, 11, 1, 1, 2, alignment=Qt.AlignHCenter)

    tab.layout.addWidget(method_label, 12, 1, 1, 2, alignment=Qt.AlignHCenter)
    tab.layout.addWidget(methods, 13, 1, 1, 2, alignment=Qt.AlignHCenter)

    tab.layout.addWidget(button_save, 14, 1, 1, 2, alignment=Qt.AlignLeft)
    tab.layout.addWidget(button_reset, 14, 1, 1, 2, alignment=Qt.AlignRight) #WYPOZYZJONOWAC

    tab.setLayout(tab.layout)

    settings_pack = {"methods": methods, "intervals": intervals, "date_start": calstart,
                     "date_stop": calstop, "currencies1": currencies_top_list1, "currencies2": currencies_top_list2,
                     "date_checkbox": date_checkbox, "currencies12": currencies_bottom_list1, 
                     "currencies21": currencies_bottom_list2} #tutaj dodac currencies bottom

    return tab, settings_pack


def create_creators_tab(close):
    """
            Functionality:
                    -Creating widget containing authors of the app.
    """
    tab = QWidget()
    tab.layout = QVBoxLayout()

    button_close = create_button(style=buttonStyleSheet, icon=QIcon(close_icon), function=close, max_size=(40, 40))

    creators_label = QLabel("Twórcy programu 'Detektor Anomalii'")
    creators_label.setStyleSheet(labelStyleSheet_big)

    olek_label = QLabel("Aleksander Forusiński - kierownik projektu, programista")
    olek_label.setStyleSheet(labelStyleSheet_not_bold)

    marcin_label = QLabel("Marcin Broś - główny programista")
    marcin_label.setStyleSheet(labelStyleSheet_not_bold)

    szymon_label = QLabel("Szymon Suchorab - interfejs użytkownika, grafika")
    szymon_label.setStyleSheet(labelStyleSheet_not_bold)

    dominika_label = QLabel("Dominika Szaradowska - interfejs użytkownika")
    dominika_label.setStyleSheet(labelStyleSheet_not_bold)

    patrycja_label = QLabel("Patrycja Stępora - interfejs użytkownika")
    patrycja_label.setStyleSheet(labelStyleSheet_not_bold)

    dawid_label = QLabel("Dawid Kunz - dokumentacja")
    dawid_label.setStyleSheet(labelStyleSheet_not_bold)

    mentor_label = QLabel("Adam Włodarczyk - Mentor biznesowy - Commerzbank")
    mentor_label.setStyleSheet(labelStyleSheet_not_bold)

    profesor_label = QLabel("prof. dr hab. inż. Adam Pelikant - pomysłodawca, opiekun projektu")
    profesor_label.setStyleSheet(labelStyleSheet_not_bold)
    
    creators_v2_label = QLabel("Druga edycja programu 'Detektor Anomalii'")
    creators_v2_label.setStyleSheet(labelStyleSheet_big)

    kuba_label = QLabel("Jakub Mijas - kierownik projektu, programista")
    kuba_label.setStyleSheet(labelStyleSheet_not_bold)

    mateusz_p_label = QLabel("Mateusz Pruss - główny programista")
    mateusz_p_label.setStyleSheet(labelStyleSheet_not_bold)

    alicja_label = QLabel("Alicja Szydłowska - główny programista")
    alicja_label.setStyleSheet(labelStyleSheet_not_bold)

    lukas_label = QLabel("Łukasz Lasowy - interfejs użytkownika, grafika")
    lukas_label.setStyleSheet(labelStyleSheet_not_bold)

    kacper_label = QLabel("Kacper Lichman - interfejs użytkownika, grafika")
    kacper_label.setStyleSheet(labelStyleSheet_not_bold)

    mateusz_o_label = QLabel("Mateusz Orski - dokumentacja")
    mateusz_o_label.setStyleSheet(labelStyleSheet_not_bold)


    horizontal_layout = QHBoxLayout()

    horizontal_layout.addWidget(creators_label, alignment=Qt.Alignment())
    horizontal_layout.addWidget(button_close, alignment=Qt.Alignment())

    tab.layout.addLayout(horizontal_layout)
    tab.layout.addWidget(QLabel(" "), alignment=Qt.Alignment())
    tab.layout.addWidget(olek_label, alignment=Qt.AlignTop)
    tab.layout.addWidget(marcin_label, alignment=Qt.AlignTop)
    tab.layout.addWidget(szymon_label, alignment=Qt.AlignTop)
    tab.layout.addWidget(dominika_label, alignment=Qt.AlignTop)
    tab.layout.addWidget(patrycja_label, alignment=Qt.AlignTop)
    tab.layout.addWidget(dawid_label, alignment=Qt.AlignTop)
    tab.layout.addWidget(mentor_label, alignment=Qt.Alignment())
    tab.layout.addWidget(profesor_label, alignment=Qt.Alignment())
    
    tab.layout.addWidget(creators_v2_label, alignment=Qt.Alignment())
    tab.layout.addWidget(kuba_label, alignment=Qt.Alignment())
    tab.layout.addWidget(mateusz_p_label, alignment=Qt.Alignment())
    tab.layout.addWidget(alicja_label, alignment=Qt.Alignment())
    tab.layout.addWidget(lukas_label, alignment=Qt.Alignment())
    tab.layout.addWidget(kacper_label, alignment=Qt.Alignment())
    tab.layout.addWidget(mateusz_o_label, alignment=Qt.Alignment())
    tab.layout.addWidget(profesor_label, alignment=Qt.Alignment())

    tab.layout.addWidget(QLabel(" "), alignment=Qt.Alignment())
    tab.layout.addWidget(QLabel(" "), alignment=Qt.Alignment())
    tab.setLayout(tab.layout)

    return tab


def create_help_tab(close):
    """
            Args:
                -close called when user clicks close button.
            Functionality:
                -Help tab to show user a description of the methods used in program.

    """
    tab = QWidget()
    tab.layout = QVBoxLayout()

    button_close = create_button(style=buttonStyleSheet, icon=QIcon(close_icon), function=close, max_size=(40, 40))

    help_label = QLabel("Pomoc")
    help_label.setStyleSheet(labelStyleSheet_big)

    help_link = "<a style=\"font-weight: normal;\" href=\"help/index.html\">Odchylenie standardowe</a>"
    help_label2 = QLabel(help_link)
    help_label2.setStyleSheet(labelStyleSheet_big)

    methods_label = QLabel("Opis metod użytych do wykrywania anomalii")
    methods_label.setStyleSheet(labelStyleSheet)

    standard_deviation_link = "<a style=\"font-weight: normal;\" href=\"https://pl.wikipedia.org/wiki/Odchylenie_standardowe\">Odchylenie standardowe</a>"
    standard_deviation_label = QLabel(standard_deviation_link)
    standard_deviation_label.setStyleSheet(labelStyleSheet)
    standard_deviation_label.setOpenExternalLinks(True)

    db_scan_link = "<a style=\"font-weight: normal;\" href=\"https://en.wikipedia.org/wiki/DBSCAN\">Grupowanie przestrzenne</a>"
    db_scan_label = QLabel(db_scan_link)
    db_scan_label.setStyleSheet(labelStyleSheet)
    db_scan_label.setOpenExternalLinks(True)

    isolation_forest_link = "<a style=\"font-weight: normal;\" href=\"https://en.wikipedia.org/wiki/Isolation_forest\">Las izolacji</a>"
    isolation_forest_label = QLabel(isolation_forest_link)
    isolation_forest_label.setStyleSheet(labelStyleSheet)
    isolation_forest_label.setOpenExternalLinks(True)

    local_outlier_link = "<a style=\"font-weight: normal;\" href=\"https://en.wikipedia.org/wiki/Local_outlier_factor\">Lokalna wartość odstająca</a>"
    local_outlier_label = QLabel(local_outlier_link)
    local_outlier_label.setStyleSheet(labelStyleSheet)
    local_outlier_label.setOpenExternalLinks(True)

    autoencoder_link = "<a style=\"font-weight: normal;\" href=\"https://en.wikipedia.org/wiki/Autoencoder\">Autoenkoder</a>"
    autoencoder_label = QLabel(autoencoder_link)
    autoencoder_label.setStyleSheet(labelStyleSheet)
    autoencoder_label.setOpenExternalLinks(True)

    horizontal_layout = QHBoxLayout()

    horizontal_layout.addWidget(help_label, alignment=Qt.Alignment())
    horizontal_layout.addWidget(button_close, alignment=Qt.Alignment())

    tab.layout.addLayout(horizontal_layout)
    tab.layout.addWidget(QLabel(" "), alignment=Qt.Alignment())
    tab.layout.addWidget(help_label2, alignment=Qt.AlignTop)
    tab.layout.addWidget(methods_label, alignment=Qt.AlignTop)
    tab.layout.addWidget(standard_deviation_label, alignment=Qt.AlignTop)
    tab.layout.addWidget(db_scan_label, alignment=Qt.AlignTop)
    tab.layout.addWidget(isolation_forest_label, alignment=Qt.AlignTop)
    tab.layout.addWidget(local_outlier_label, alignment=Qt.AlignTop)
    tab.layout.addWidget(autoencoder_label, alignment=Qt.AlignTop)

    tab.layout.addWidget(QLabel(" "), alignment=Qt.Alignment())
    tab.layout.addWidget(QLabel(" "), alignment=Qt.Alignment())
    tab.layout.addWidget(QLabel(" "), alignment=Qt.Alignment())
    tab.layout.addWidget(QLabel(" "), alignment=Qt.Alignment())
    tab.setLayout(tab.layout)

    return tab


def read_settings_from_file():
    """
            Functionality:
                   -reading content of setting file.
                   -extracting values from each line
            Returns:
                   -returning dictionary which contains different key-valuepairs
    """
    f = open('settings', "r").readlines()
    settings = []
    for line in f:
        settings.append(line.split(':')[1][:-1])

    return {"currencies1": settings[0], "currencies2": settings[1], "methods": settings[2],
            "intervals": settings[3], "date_start": settings[4], "date_stop": settings[5], "date_checkbox": settings[6], 
            "currencies12": settings[7], "currencies21": settings[8]}


def create_button(text="", style="", icon=None, function=None, min_size=None, max_size=None):
    """
            Args:
                -text (str): The text to be displayed on the button. Default is an empty string.
                -style (str): The CSS style to be applied to the button. Default is an empty string.
                -icon (QIcon): The icon to be displayed on the button. Default is None.
                -function (function): The function to be called when the button is clicked. Default is None.
                -min_size (tuple of ints): The minimum size of the button. Default is None.
                -max_size (tuple of ints): The maximum size of the button. Default is None.
            Returns:
                -button (QPushButton): The created button widget.
            Functionality:
                -creating button
            """
    button = QPushButton(text)
    button.setStyleSheet(style)
    if icon is not None:
        button.setIcon(icon)
    if function is not None:
        button.clicked.connect(function)
    if min_size is not None:
        button.setMinimumSize(min_size[0], min_size[1])
    if max_size is not None:
        button.setMaximumSize(max_size[0], max_size[1])

    return button


def create_calendar(widget):
    """
            Args:
                -widget (class) representing a widget type.
            Functionality:
                -creating calendar widget.
            """
    calendar = widget()

    return calendar
