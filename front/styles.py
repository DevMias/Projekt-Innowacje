buttonStyleSheet = """
QPushButton {
    background-color: #2B5DD1;
    color: #FFFFFF;
    border-style: outset;
    padding: 2px;
    font: bold 20px;
    border-width: 6px;
    border-radius: 10px;
    border-color: #2752B8;
}
QPushButton:pressed {
    background-color: #193984;
}
"""

DateEditStyleSheet = """
QDateEdit
{
    border: 1px solid gray;
    border-radius: 3px;
    background-color : white;
    padding : 2px;
    font: 15px;
}
    
QDateEdit::down-arrow
{
    image: url(icons/arrow_down.png);
}
"""

comboBoxStyleSheet = """
QComboBox {
    border: 1px solid gray;
    border-radius: 3px;
    padding: 1px 18px 1px 3px;
    min-width: 6em;
    border-color: gray;
    font: 15px;
    color: #000000;
    background-color: #FFFFFF;
}

QComboBox::down-arrow {
    image: url(icons/arrow_down.png);
}
"""

labelStyleSheet = """
QLabel {
    padding: 2px;
    font: bold 15px;
}

QLineEdit {
    padding: 2px;
    font: 15px;
}
"""

labelStyleSheet_red = """
QLabel {
    padding: 2px;
    font: bold 15px;
    color: red;
}
"""

labelStyleSheet_orange = """
QLabel {
    padding: 2px;
    font: bold 15px;
    color: orange;
}
"""

labelStyleSheet_yellow = """
QLabel {
    padding: 2px;
    font: bold 15px;
    color: #FEE227;
}
"""

labelStyleSheet_light_green = """
QLabel {
    padding: 2px;
    font: bold 15px;
    color: lightGreen;
}
"""

labelStyleSheet_green = """
QLabel {
    padding: 2px;
    font: bold 15px;
    color: green;
}
"""

labelStyleSheet_big = """
QLabel {
    padding: 2px;
    font: bold 30px;
}
"""

labelStyleSheet_not_bold = """
QLabel {
    padding: 2px;
    font: 15px;
}
"""

tabStyleSheet = """
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
