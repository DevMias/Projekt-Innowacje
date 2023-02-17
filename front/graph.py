import pyqtgraph as pg

from front.styles import labelStyleSheet_red, labelStyleSheet, labelStyleSheet_yellow, labelStyleSheet_orange,\
    labelStyleSheet_green, labelStyleSheet_light_green, method_properties as mp
from backend.backend_functions import run_method
import pandas as pd

class Graph:
    """
            Args:
                -method (str): The plot method to use, which can be one of the following: 'plot', 'scatter', or 'bar'.
                -csv (DataFrame): The Pandas DataFrame containing the dataset to plot.
                -date (str): The name of the date column in the dataset.
                -target (str): The name of the target variable column in the dataset.
                -label (QLabel): The QLabel object used to display the current date range of the plot.
                -slider (QSlider): The QSlider object used to adjust the current date range of the plot.
                -slider_label (QLabel): The QLabel object used to display the current value of the slider.
                -checkbox (QCheckBox): The QCheckBox object used to toggle the display of anomalies on the plot.
                -date_label (QLabel): The QLabel object used to display the current date value of the plot.
                -value_label (QLabel): The QLabel object used to display the current value of the target variable on the plot.
                -currency1 (str, optional): The name of the first currency, used to generate the plot title. Default is set to "".
                -currency2 (str, optional): The name of the second currency, used to generate the plot title. Default is set to "".
                -title (str, optional): The title of the plot. Default is set to "".
                -with_anomalies (bool, optional): Whether to include anomalies on the plot. Default is set to False.
            Functionality:
                -Class for creating and updating the PyqtGraph plot with specified methods, datasets, date ranges and allows for user interactions.
    """
    def __init__(self, method, csv, date, target, label, slider, slider_label, checkbox, date_label, value_label,
                 currency1="", currency2="", title="", with_anomalies=False):
        self.proxy = None
        self.flipped = False
        self.multiplayer = 1
        self.refresh = False
        self.anomalies_list = ["Anomaly_1", "Anomaly_2", "Anomaly_3", "Anomaly_4", "Anomaly_5"]
        self.graph = pg.PlotWidget()
        self.an_graph = None
        self.method = method
        self.csv = csv
        self.title = title
        self.pen = pg.mkPen("b", width=2)
        self.target = target
        self.anomalies = []
        self.anomalies_to_download = None
        self.date = date
        self.date_range = (self.csv[self.date][0], self.csv[self.date][len(self.csv[self.date]) - 1])
        self.data_indexes = (0, len(self.csv[self.date]))
        self.date_label_range = label
        self.date_label_range.setText("Zakres dat: od " + self.date_range[0] + " do " + self.date_range[1])
        self.date_label_range.update()
        self.with_anomalies = with_anomalies
        self.checkbox = checkbox
        self.currency1 = currency1
        self.currency2 = currency2
        self.slider = slider
        self.slider_label = slider_label
        self.date_label = date_label
        self.value_label = value_label

        self.checkbox.stateChanged.connect(self.update_graph)

        if self.title == "" and currency1 != "" and currency2 != "":
            self.title = currency1 + '/' + currency2

        mult = len(self.csv[self.date]) // 9 if len(self.csv[self.date]) > 9 else 1
        x_ticks_dict = {}
        for i in range(0, len(self.csv[self.date]) // mult + 1):
            if i * mult < len(self.csv[self.date]):
                x_ticks_dict[i * mult] = self.csv[self.date][i * mult]

        self.x_ticks = x_ticks_dict.items()

        self.init_graph()

    def init_graph(self):
        """
                    Funcionality:
                            -setting up mouse movement with ps.SignalProxy.
                            -adjusting graph.
                            -filtering csv file.
                            -if anomalies are not being displayed connect 'udpate_graph'.
                            -plotting financial data.
                            -running anomalies.
                            -when 'Wszystkie' method is chosen plot each type of anomaly.
                            -when anomaly is detected plot those oon red.
        """
        self.proxy = pg.SignalProxy(self.graph.scene().sigMouseMoved, rateLimit=60, slot=self.update_crosshair)

        if self.flipped:
            self.flip()

        if self.method == "Grupowanie przestrzenne":
            self.slider.setValue(50)
        if self.method == "Las izolacji":
            self.slider.setValue(20)
            self.multiplayer = 2
        if self.method == "Lokalna wartość odstająca":
            self.slider.setValue(25)
            self.multiplayer = 2

        self.slider_label.setText("Czułość metody: " + str(self.slider.value()) + "%")

        if not self.with_anomalies:
            self.csv = self.csv[[self.date, self.target]]
        else:
            if self.method == "Wszystkie":
                self.csv = self.csv[[self.date, self.target, 'Anomaly_1', 'Anomaly_2', 'Anomaly_3', 'Anomaly_4',
                                     'Anomaly_5']]
            else:
                self.csv = self.csv[[self.date, self.target, 'Anomaly']]
        self.csv = self.csv.rename(columns={self.target: "Exchange", self.date: "Date"})
        self.date = "Date"
        self.target = "Exchange"

        self.graph.setBackground('w')
        self.graph.setTitle(self.title)
        self.graph.setXRange(0, len(self.csv[self.date]))
        self.graph.setYRange(min(self.csv[self.target]), max(self.csv[self.target]))
        x_axis = self.graph.getAxis("bottom")
        x_axis.setTicks([self.x_ticks])

        if not self.with_anomalies:
            self.graph.sigRangeChanged.connect(self.update_graph)
            self.graph.sigSceneMouseMoved.connect(self.update_graph)

        self.graph.plot(self.csv.index, self.csv[self.target], pen=self.pen)

        if not self.with_anomalies:
            anomaly_detected_data = run_method([self.csv], self.target, self.date, self.method,
                                               self.slider.value() / 100 / self.multiplayer)
        else:
            anomaly_detected_data = self.csv

        self.anomalies_to_download = anomaly_detected_data

        if self.method == "Wszystkie":
            if anomaly_detected_data is not None:
                self.graph.addLegend()

                self.anomalies = []
                for anomalies in self.anomalies_list:
                    anomaly = anomaly_detected_data.loc[anomaly_detected_data[anomalies] == True, ['Exchange']]
                    temp = pd.concat([pd.Series(0), anomaly])
                    self.anomalies.append(temp[['Exchange']])

                self.graph.plot(self.csv.index, self.csv[self.target], pen=self.pen)

                for anomalies, method in zip(self.anomalies, mp):
                    self.an_graph = self.graph.plot(anomalies.index, anomalies["Exchange"], pen=None,
                                                    symbol='o', symbolSize=5, symbolPen=mp[method]['color'],
                                                    symbolBrush=mp[method]['color'], name=mp[method]['polish_name'])

                self.graph.showGrid(x=True, y=False, alpha=1.0)

        else:
            if anomaly_detected_data is not None:
                anomalies = anomaly_detected_data.loc[anomaly_detected_data['Anomaly'] == True, ['Exchange']]
                temp = pd.concat([pd.Series(0), anomalies])
                self.anomalies = temp['Exchange']
                self.an_graph = self.graph.plot(self.anomalies.index, self.anomalies, pen=None, symbol='o',
                                                symbolSize=5, symbolPen='r', symbolBrush='r')

                self.graph.showGrid(x=True, y=False, alpha=1.0)

    def update_graph(self):
        """
                Funcionality:
                    -updating slider bar to relfect slider's current value.
                    -determining current x-axis range based on the axis object and size of the CSV data
        """
        self.slider_label.setText("Czułość metody: " + str(self.slider.value()) + "%")
        ax = self.graph.getAxis('bottom')

        if ax.range[0] >= 0:
            x1 = int(round(ax.range[0], 0))
        else:
            x1 = 0

        if ax.range[0] <= ax.range[1] < len(self.csv[self.date]) - 1:
            x2 = int(round(ax.range[1], 0))
        else:
            x2 = len(self.csv[self.date]) - 1

        if x2 > 1 and x1 < x2 - 1:
            self.data_indexes = (x1, x2 + 1)

            self.date_range = (self.csv[self.date][x1], self.csv[self.date][x2])
            self.date_label_range.setText("Zakres dat: od " + self.date_range[0] + " do " + self.date_range[1])
            self.date_label_range.update()

            mult = (x2 - x1) // 9 if (x2 - x1) > 9 else 1
            x_ticks_dict = {}
            for i in range(0, x2 // mult + 1):
                if i * mult < len(self.csv[self.date]):
                    x_ticks_dict[i * mult] = self.csv[self.date][i * mult]

            self.x_ticks = x_ticks_dict.items()
            x_axis = self.graph.getAxis("bottom")
            x_axis.setTicks([self.x_ticks])

            zoom_level = len(self.csv[self.date]) // (x2 - x1)
            zoom_level = 7 if zoom_level > 7 else zoom_level

            anomaly_detected_data = None
            if self.checkbox.isChecked() or self.refresh:
                anomaly_detected_data = run_method([self.csv[x1:x2]], self.target, self.date, self.method,
                                                   self.slider.value() / 100 / self.multiplayer)

            if self.method == "Wszystkie":
                if anomaly_detected_data is not None and (self.checkbox.isChecked() or self.refresh):

                    self.anomalies = []
                    for anomalies in self.anomalies_list:
                        anomaly = anomaly_detected_data.loc[anomaly_detected_data[anomalies] == True, ['Exchange']]
                        temp = pd.concat([pd.Series(0), anomaly])
                        self.anomalies.append(temp[['Exchange']])

                self.graph.clear()
                self.graph.addLegend()

                self.graph.plot(self.csv.index, self.csv[self.target], pen=self.pen)

                for anomalies, color, method in zip(self.anomalies, mp):
                    if len(self.anomalies) > 1:
                        self.an_graph = self.graph.plot(anomalies.index, anomalies["Exchange"], pen=None,
                                                        symbol='o', symbolSize=5 + zoom_level, symbolPen=mp[method]['color'],
                                                        symbolBrush=mp[method]['color'], name=mp[method]['polish_name'])

                self.graph.setYRange(min(self.csv[self.target][x1:x2]), max(self.csv[self.target][x1:x2]))
            else:
                if anomaly_detected_data is not None and (self.checkbox.isChecked() or self.refresh):
                    self.anomalies = anomaly_detected_data.loc[anomaly_detected_data['Anomaly'] == True, ['Exchange']]

                    temp = pd.concat([pd.Series(0), self.anomalies])
                    self.anomalies = temp['Exchange']

                self.graph.clear()

                self.graph.plot(self.csv.index, self.csv[self.target], pen=self.pen)
                if len(self.anomalies) > 1:
                    self.an_graph = self.graph.plot(self.anomalies.index, self.anomalies, pen=None,
                                                    symbol='o', symbolSize=5 + zoom_level, symbolPen='r',
                                                    symbolBrush='r')

                self.graph.setYRange(min(self.csv[self.target][x1:x2]), max(self.csv[self.target][x1:x2]))

        else:
            self.graph.clear()
            self.an_graph = self.graph.plot([0, 1], [0, 0], pen=self.pen)

        self.refresh = False

    def flip(self):
        """
                Args:

                    -self: the MainWindow instance

                Functionality:
                    -flip method flips the currency pair and the corresponding values of the csv dataframe in the MainWindow class.
                    If the currency1 and currency2 attributes have been set, it swaps them and updates the title of the graph with the new currency pair.
                    It also calculates the inverse values of the target column of the csv dataframe (i.e. the exchange rates) and updates them in the dataframe.
                    Finally, it refreshes the graph with the new data.

        """
        self.flipped = not self.flipped

        if self.currency1 is not None and self.currency2 is not None:
            self.title = self.currency2 + '/' + self.currency1
            self.graph.setTitle(self.title)
            temp = self.currency1
            self.currency1 = self.currency2
            self.currency2 = temp

        for idx in self.csv.index:
            self.csv.loc[idx, self.target] = 1 / self.csv[self.target][idx] if self.csv[self.target][idx] != 0 else 0

        self.refresh_graph()

    def reset_slider(self):
        """
                Reseting the value of the slider to a default value based on the current method selected in the GUI, and then refreshing the graph.
        """
        if self.method == "Grupowanie przestrzenne":
            self.slider.setValue(50)
        if self.method == "Las izolacji":
            self.slider.setValue(20)
        if self.method == "Lokalna wartość odstająca":
            self.slider.setValue(25)

        self.refresh_graph()

    def refresh_graph(self):
        """
            Refreshes graph.
        """
        self.refresh = True
        self.update_graph()

    def reset_graph(self):
        """
            Reset graph to default values.
        """
        self.checkbox.setChecked(True)
        self.init_graph()
        self.update_graph()

    def update_crosshair(self, e):
        """
            The update_crosshair method is used to update the crosshair in the graph whenever the mouse is moved over it.
            It takes an event e as input and uses the position pos of the mouse to calculate the corresponding x and y values in the plot.

            If the x value is within the range of the available data, the method checks whether the selected method is "Wszystkie"  or a specific one.
            Based on that, it updates the color of the date and value labels to indicate whether the selected data point is an anomaly or not.

            The date and value labels are then updated with the corresponding data point's date and value.
        """
        pos = e[0]
        if self.graph.sceneBoundingRect().contains(pos):
            mouse_point = self.graph.getPlotItem().vb.mapSceneToView(pos)

            if 0 <= int(round(mouse_point.x())) < len(self.csv[self.date]):
                if self.method != "Wszystkie":
                    if int(round(mouse_point.x())) in self.anomalies.index:
                        self.date_label.setStyleSheet(labelStyleSheet_red)
                        self.value_label.setStyleSheet(labelStyleSheet_red)
                    else:
                        self.date_label.setStyleSheet(labelStyleSheet)
                        self.value_label.setStyleSheet(labelStyleSheet)
                else:
                    if int(round(mouse_point.x())) in self.anomalies[4].index:
                        self.date_label.setStyleSheet(labelStyleSheet_red)
                        self.value_label.setStyleSheet(labelStyleSheet_red)
                    elif int(round(mouse_point.x())) in self.anomalies[3].index:
                        self.date_label.setStyleSheet(labelStyleSheet_orange)
                        self.value_label.setStyleSheet(labelStyleSheet_orange)
                    elif int(round(mouse_point.x())) in self.anomalies[2].index:
                        self.date_label.setStyleSheet(labelStyleSheet_yellow)
                        self.value_label.setStyleSheet(labelStyleSheet_yellow)
                    elif int(round(mouse_point.x())) in self.anomalies[1].index:
                        self.date_label.setStyleSheet(labelStyleSheet_light_green)
                        self.value_label.setStyleSheet(labelStyleSheet_light_green)
                    elif int(round(mouse_point.x())) in self.anomalies[0].index:
                        self.date_label.setStyleSheet(labelStyleSheet_green)
                        self.value_label.setStyleSheet(labelStyleSheet_green)
                    else:
                        self.date_label.setStyleSheet(labelStyleSheet)
                        self.value_label.setStyleSheet(labelStyleSheet)

                self.date_label.setText("Data: " + str(self.csv[self.date][int(round(mouse_point.x()))]))
                self.value_label.setText("Wartość: " + str(round(self.csv[self.target][int(round(mouse_point.x()))], 7)))