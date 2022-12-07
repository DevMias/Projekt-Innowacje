from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QLineEdit, QHBoxLayout, QComboBox, QDateEdit, \
    QCheckBox, QGridLayout
from backend import backend_functions as backend
from front.styles import buttonStyleSheet, labelStyleSheet, comboBoxStyleSheet, currencies_list, DateEditStyleSheet, \
    flag_list, labelStyleSheet_big, labelStyleSheet_not_bold, important_icon, close_icon


def create_graph_tab(close, pack_fun, methods_list, file, important):
    """
    It creates a tab for the graph

    :param close: function that closes the tab
    :param pack_fun: function that will be called when the button is pressed
    :param methods_list: list of methods to choose from
    :param file: path to the file
    :param important: function that will be called when the user clicks the "important" button
    :return: A tuple of two elements (QWidget, dict)
    """
    csv_data, error1 = backend.download_csv(file, from_file=True)

    if error1 == "empty":
        backend.error("Błedny plik", "Wprowadzony plik jest pusty lub posiada zbyt mało danych")

    if csv_data is None:
        return None, None

    columns = csv_data.columns.tolist()

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

    target_column = QComboBox()
    target_column.setStyleSheet(comboBoxStyleSheet)

    for column in columns:
        target_column.addItem(column)

    target_column.setCurrentText("Exchange")
    tab.layout.addWidget(target_column, alignment=Qt.Alignment())

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

    pack = {"method": methods, "csv": csv_data, "title": title, "date": date_column, "target": target_column,
            "format1": date_format_box1, "format2": date_format_box2, "format3": date_format_box3}

    return tab, pack


def create_settings_tab(method_list, interval_list, close, save, reset):
    """
    It creates a tab with settings for the program

    :param method_list: list of methods
    :type list of Strings
    :param interval_list: list of intervals
    :type list of Strings
    :param close: function that closes the window
    :type function object to specify buttons action
    :param save: function that saves the settings
    :type function object to specify buttons action
    :param reset: function that resets the settings to default
    :type function object to specify buttons action
    :return: A tuple of two elements:
        1. A QWidget object, aka whole tab
        2. A dictionary of QWidgets, pack that contains all settings of tab
    """
    settings = read_settings_from_file()    # dictionary with settings

    tab = QWidget()
    tab.layout = QVBoxLayout()

    # calendars for setting dates
    calendar_start_label = QLabel("Data początkowa")
    calendar_start_label.setStyleSheet(labelStyleSheet)
    calendar_stop_label = QLabel("Data końcowa")
    calendar_stop_label.setStyleSheet(labelStyleSheet)

    calendar_start = QDateEdit()
    calendar_start.setCalendarPopup(True)
    calendar_start.setStyleSheet(DateEditStyleSheet)
    calendar_stop = QDateEdit()
    calendar_stop.setCalendarPopup(True)
    calendar_stop.setStyleSheet(DateEditStyleSheet)

    if settings["date_checkbox"] == "False":
        calendar_start.setDate(backend.string_to_date(settings["date_start"]))
        calendar_stop.setDate(backend.string_to_date(settings["date_stop"]))
    else:
        calendar_start.setDate(QDate.currentDate().addYears(-1))
        calendar_stop.setDate(QDate.currentDate())

    method_label = QLabel("Metoda")
    method_label.setStyleSheet(labelStyleSheet)
    methods = QComboBox()
    methods.setStyleSheet(comboBoxStyleSheet)

    # intervals
    interval_label = QLabel("Interwał")
    interval_label.setStyleSheet(labelStyleSheet)
    intervals = QComboBox()
    intervals.setStyleSheet(comboBoxStyleSheet)

    # currencies
    currencies_label = QLabel("Waluty")
    currencies_label.setStyleSheet(labelStyleSheet)
    currencies1 = QComboBox()
    currencies1.setStyleSheet(comboBoxStyleSheet)
    currencies2 = QComboBox()
    currencies2.setStyleSheet(comboBoxStyleSheet)

    # lists for currencies
    for flag, currency in zip(flag_list, currencies_list):
        currencies1.addItem(QIcon(flag), currency)
        currencies2.addItem(QIcon(flag), currency)

    # currencies1.setCurrentText(settings["currencies1"])
    currencies1.setCurrentIndex(int(settings["currencies1"]))
    # currencies2.setCurrentText(settings["currencies2"])
    currencies2.setCurrentIndex(int(settings["currencies2"]))

    # list for intervals
    interval_image = ["numbers/" + name + ".png" for name in interval_list]

    for image, interval in zip(interval_image, interval_list):
        intervals.addItem(QIcon(image), interval)

    # intervals.setCurrentText(settings["intervals"])
    intervals.setCurrentIndex(int(settings["intervals"]))

    # setting names for methods in combo box
    for method in method_list:
        methods.addItem(method)

    # methods.setCurrentText(settings["methods"])
    methods.setCurrentIndex(int(settings["methods"]))   # set default method on index taken from settings file

    # reload (reset) current settings to settings from file
    button_reset = create_button(style=buttonStyleSheet, text="Resetuj", function=reset, max_size=(150, 40))

    # close setting_tab
    button_close = create_button(style=buttonStyleSheet, icon=QIcon(close_icon), function=close, max_size=(40, 40))

    default_label = QLabel("Ustawienia wartości domyślnych")
    default_label.setStyleSheet(labelStyleSheet)

    date_checkbox = QCheckBox()
    date_checkbox.setText("Ostatni rok")
    date_checkbox.setChecked(True)

    # writing current settings to file named 'settings'
    button_save = create_button(style=buttonStyleSheet, text="Zapisz", function=save, min_size=(150, 40))

    tab.layout = QGridLayout()
    tab.layout.setSpacing(10)
    tab.layout.addWidget(default_label, 1, 0)
    tab.layout.addWidget(button_reset, 1, 1, alignment=Qt.Alignment())
    tab.layout.addWidget(button_close, 1, 2, alignment=Qt.Alignment())
    tab.layout.addWidget(currencies_label, 2, 0, 1, 3)
    tab.layout.addWidget(currencies1, 3, 0, 1, 3)
    tab.layout.addWidget(currencies2, 4, 0, 1, 3)
    tab.layout.addWidget(calendar_start_label, 5, 0, 1, 3)
    tab.layout.addWidget(calendar_start, 6, 0, 1, 3)
    tab.layout.addWidget(calendar_stop_label, 7, 0, 1, 3)
    tab.layout.addWidget(calendar_stop, 8, 0, 1, 3)
    tab.layout.addWidget(date_checkbox, 9, 0, 1, 3)
    tab.layout.addWidget(interval_label, 10, 0, 1, 3)
    tab.layout.addWidget(intervals, 11, 0, 1, 3)
    tab.layout.addWidget(method_label, 12, 0, 1, 3)
    tab.layout.addWidget(methods, 13, 0, 1, 3)
    tab.layout.addWidget(button_save, 14, 0, 1, 3)

    tab.setLayout(tab.layout)

    settings_pack = {"methods": methods, "intervals": intervals, "date_start": calendar_start,
                     "date_stop": calendar_stop, "currencies1": currencies1, "currencies2": currencies2,
                     "date_checkbox": date_checkbox}

    return tab, settings_pack


def create_creators_tab(close):
    """
    This function creates a tab in the GUI

    :param close: The function to call when the user clicks the close button
    :type function
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

    tab.layout.addWidget(QLabel(" "), alignment=Qt.Alignment())
    tab.layout.addWidget(QLabel(" "), alignment=Qt.Alignment())
    tab.setLayout(tab.layout)

    return tab

@DeprecationWarning
def create_help_tab(close):
    """
    > This function creates a help tab in the GUI

    :param close: The function to call when the user clicks the close button
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


def read_settings_from_file() -> dict:
    # TODO The same name of function like name of method in main.py
    """
    It reads the settings from a file and return dictionary with settings
    """
    f = open('settings', "r").readlines()
    settings = []
    for line in f:
        settings.append(line.split(':')[1][:-1])

    return {"currencies1": settings[0], "currencies2": settings[1], "methods": settings[2],
            "intervals": settings[3], "date_start": settings[4], "date_stop": settings[5], "date_checkbox": settings[6]}


def create_button(text="", style="", icon=None, function=None, min_size=None, max_size=None):
    """
    This function creates a button with the given text, style, icon, function, min_size, and max_size

    :param text: The text that will be displayed on the button
    :param style: This is the style of the button predefined in 'style.py'
    :param icon: The icon to be displayed on the button
    :param function: The function to be called when the button is clicked
    :param min_size: The minimum size of the button
    :param max_size: The maximum size of the button
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
