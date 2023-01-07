font_color = 'red'
hover_color = 'rgb(28, 185, 199)'
gray_color = 'rgb(75, 78, 82)'
font_size_20 = '20px'
font_size_30 = '30px'
font_size_15 = '15px'
buttonStyleSheet = f"""
QPushButton {{ 
    background-color: rgb(75, 78, 82);
    color: {font_color};
    padding: 2px;
    font: {font_size_20};
    border: 1px inset rgb(24, 26, 25);
    border-radius: 10px;
    width:60px;
}}
QPushButton:hover {{
    background-color: {hover_color};
}}
#year_checkbox{{
    font-size:{font_size_20};
    color: {font_color};
    text-transform: uppercase;
    font-family: "Calibri", Times, serif;
}}
"""

swapButtonStyleSheet = f"""
QPushButton {{
    background-color: {gray_color};
    color:{font_color};
    padding: 15px;
    font: {font_size_20};
    border: 1px inset rgb(24, 26, 25);
    border-radius: 10px;
}}
QPushButton:hover {{
    background-color: {hover_color};
}}
"""

generatePlotButtonStyleSheet = f"""
QPushButton {{ 
    background-color: {gray_color};
    color:{font_color};
    padding: 10px;
    font: bold {font_size_20};
    border: 1px inset rgb(24, 26, 25);
    border-radius: 10px;
}}
QPushButton:hover {{
    background-color: {hover_color};
}}
"""

DateEditStyleSheet = f"""
QDateEdit
{{
    color:{font_color};
    border-radius: 3px;
    border: 1px solid rgb(24, 26, 25);
    font: {font_size_20};
    background-color:rgb(75, 78, 82);
    text-align:center;
    margin-left: 5px;
    padding:4px;
}}

#settings_element{{
    max-width:600px;
    min-width:400px;
    text-align:center;
    background-color:{gray_color};
    border: 1px solid rgb(24, 26, 25);
}}

QDateEdit::down-arrow
{{
    image: url(icons/arrow_down.png);
}}
QDateEdit::drop-down {{
    width: 28px;
}}
"""

calendarStyleSheet = f"""
QCalendarWidget QWidget{{
    alternate-background-color: #6e6e70;
    color: #fbfbfb;
}}
QCalendarWidget QToolButton#qt_calendar_prevmonth{{
    qproperty-icon: url(icons/left_arrow.png);
}}
QCalendarWidget QToolButton#qt_calendar_nextmonth{{
    qproperty-icon: url(icons/right_arrow.png);
}}
QCalendarWidget QToolButton:hover{{
    background-color: {hover_color};
}}
QCalendarWidget QAbstractItemView:enabled{{
    background-color: #212121;
    color: #fbfbfb;
    selection-background-color: rgb(28, 185, 199);
    selection-color: green;
}}
"""

comboBoxStyleSheet = f"""
QComboBox {{
    color:{font_color};
    border: 1px solid rgb(24, 26, 25);
    padding: 1px 18px 1px 3px;
    min-width: 6em;
    font: 18px;
    background-color: rgb(75, 78, 82);
    margin-left: 5px;
    padding:4px;
}}
QComboBox QAbstractItemView{{ /* Stylowanie drop-down menu */
    color:{font_color};
}}
#settings_element{{
    max-width:500px;
    min-width:500px;
    text-align:center;  
    border: 1px solid rgb(24, 26, 25);
    background-color:{gray_color};
}}
QComboBox::down-arrow {{
    image: url(icons/arrow_down.png);
}}
QComboBox::drop-down {{
    width: 28px;
}}
"""

labelStyleSheet = f"""
QLabel {{
    border: 0;
    padding: 2px;
    font: bold {font_color};
    text-transform:uppercase;
    color:{font_color};
}}
QLabel#graph_title {{
    margin-top: 20px;
    color:{font_color};
}}
#graph_fields{{
    margin: 0 auto;
    text-align: right;
}}

QLineEdit {{
    color:{font_color};
    padding: 8px;
    border: 0;
    border-bottom: 1px solid rgb(169, 167, 169);
    background-color:rgb(67, 66, 67);
    font: {font_size_15}
}}
#default_label{{
    margin-left:200px; /* label z settingsow */
}}
"""

labelStyleSheet_red = f"""
QLabel {{
    padding: 2px;
    font: bold {font_size_15};
    color:{font_color};
}}
"""

labelStyleSheet_orange = f"""
QLabel {{
    padding: 2px;
    font: bold {font_size_15};
    color: orange;
}}
"""

labelStyleSheet_yellow = f"""
QLabel {{
    padding: 2px;
    font: bold {font_size_15};
    color: #FEE227;
}}
"""

labelStyleSheet_light_green = f"""
QLabel {{
    padding: 2px;
    font: bold {font_size_15};
    color: lightGreen;
}}
"""

settingsLayoutStyleSheet = f"""
QPushButton{{
    width:64px;
}}
"""

labelStyleSheet_green = f"""
QLabel {{
    padding: 2px;
    font: bold {font_size_15};
    color: green;
}}
"""

labelStyleSheet_big = f"""
QLabel {{
    color:{font_color};
    padding: 2px;
    font: bold {font_size_30};
}}
"""

labelStyleSheet_not_bold = f"""
QLabel {{
    color:{font_color};
    padding: 2px;
    font: {font_size_15};
}}
"""

mainTabStyleSheet = f"""
    QWidget {{
        background-color: #393939;
    }}
    QTabWidget{{
        border:2px solid #939393;
        min-width:80px;
        height:18px;
        padding:20px;
        font-weight:bold;
        font-size:{font_size_15};
    }}
    QTabWidget::pane{{
        border: none; /* tu byl ten border zepsuty*/
    }}
    QTabBar::tab{{
        color:{font_color};
        background-color:rgb(82, 82, 82);
        font-weight:normal;
    }}
    QTabBar::tab:selected {{ 
        color:black;
        background-color: rgb(242, 242, 242);
        min-width:80px;
        height:18px;
        padding:10px;
        font-weight:bold;
        font-size:16px;
    }}
"""

windowStyleSheet = f"""
QWidget {{
    color:{font_color};
    background-color: #323232;
    font-family: "Calibri", Times, serif;
}}
QWidget:hover{{
    color:black;
}}
QLabel{{
    border:0;
    padding: 10px;
    font-family: "Calibri", Times, serif;
}}
"""

swap_icon = "icons/swap.png"

app_logo = "icons/appLogo.png"

settings_icon = "icons/settings.png"
close_icon = "icons/close.png"

important_icon = "icons/star.png"
not_important_icon = "icons/blank.png"

currencies_list = ["BTC - Bitcoin", "GBP - Funt Brytyjski", "AUD - Dolar Australijski", "CHF - Frank Szwajcarski",
                   "EUR - Euro", "USD - Dolar Amerykański", "PLN - Polski Złoty", "ARS - Peso Argentyńskie",
                   "CNY - Renmibi", "HKD - Dolar Hongkongu", "IDR - Rupia Indonezyjska", "ILS - Nowy Izraelski Szekel",
                   "XAG - Srebro", "XAU - Złoto", "XPD - Uncja Palladu", "XPT - Uncja Platyny", "TRY - Lira Turecka",
                   "XDR - Specjalne Prawa Ciągnienia", "EGP - Funt Egipski", "NAD - Dolar Namibijski", "ZAR - Rand",
                   "UAH - Hrywna", "BRL - Real Brazylijski", "CAD - Dolar Kanadyjski", "CLP - Peso Chilijskie",
                   "MXN - Peso Meksykańskie", "INR - Rupia Indyjska", "JPY - Jen", "KRW - Won Południowokoreański",
                   "MYR - Ringgit", "NZD - Dolar Nowozelandzki", "PHP - Peso Filipińskie", "SGD - Dolar Singapurski",
                   "THB - Bat Tajlandzki", "TWD - Dolar Tajwański", "BGN - Lew Bułgarski", "CZK - Korona Czeska",
                   "DKK - Korona Duńska", "HRK - Kuna Chorwacka", "HUF - Forint", "ISK - Korona Islandzka",
                   "NOK - Korona Norweska", "RON - Lej Rumuński", "RUB - Rubel Rosyjski", "SEK - Korona Szwedzka"]

currencies_list.sort()
start_currency1 = "PLN - Polski Złoty"
start_currency2 = "EUR - Euro"

flag_list = ["flags/" + name[:3] + ".png" for name in currencies_list]
