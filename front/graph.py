import pyqtgraph as pg

from front.styles import labelStyleSheet_red, labelStyleSheet, labelStyleSheet_yellow, labelStyleSheet_orange, \
    labelStyleSheet_green, labelStyleSheet_light_green
from backend.backend_functions import run_method
from backend.differential_anomalies import get_anomalies
import pandas as pd

list_of_colors = [(255, 0, 0), (255, 167, 0), (255, 244, 0), (163, 255, 0), (44, 186, 0)]
list_of_colors.reverse()
list_legend = ["1 metoda", "2 metody", "3 metody", "4 metody", "5 metod"]


class Graph:
    def __init__(self, method, csv, date, target, label, slider, slider_label, checkbox, date_label, value_label,
                 currency1="", currency2="", title="", with_anomalies=False, differential=False):
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
        self.differential = differential

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
        if self.method == 'Analiza Różnicowa':
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
        if self.differential:
            anomaly_detected_data = get_anomalies([self.csv], self.target,self.method, self.date)
        else:
            if not self.with_anomalies:
                anomaly_detected_data = run_method([self.csv], self.target, self.date, self.method,
                                                   self.slider.value() / 100 / self.multiplayer)
            else:
                anomaly_detected_data = run_method([self.csv], self.target, self.date, self.method,
                                                   self.slider.value() / 100 / self.multiplayer)
                # anomaly_detected_data = self.csv

        self.anomalies_to_download = anomaly_detected_data
        print(anomaly_detected_data)
        if self.method == "Wszystkie":
            if anomaly_detected_data is not None:
                self.graph.addLegend()

                self.anomalies = []
                for anomalies in self.anomalies_list:
                    anomaly = anomaly_detected_data.loc[anomaly_detected_data[anomalies] == True, ['Exchange']]
                    temp = pd.concat([pd.Series(0), anomaly])
                    self.anomalies.append(temp[['Exchange']])

                self.graph.plot(self.csv.index, self.csv[self.target], pen=self.pen)

                for anomalies, color, legend in zip(self.anomalies, list_of_colors, list_legend):
                    self.an_graph = self.graph.plot(anomalies.index, anomalies["Exchange"], pen=None, symbol='o',
                                                    symbolSize=5, symbolPen=color, symbolBrush=color, name=legend)

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

                for anomalies, color, legend in zip(self.anomalies, list_of_colors, list_legend):
                    if len(self.anomalies) > 1:
                        self.an_graph = self.graph.plot(anomalies.index, anomalies["Exchange"], pen=None,
                                                        symbol='o', symbolSize=5 + zoom_level, symbolPen=color,
                                                        symbolBrush=color, name=legend)

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
        self.flipped = not self.flipped

        if self.currency1 != "" and self.currency2 != "":
            self.title = self.currency2 + '/' + self.currency1
            self.graph.setTitle(self.title)
            temp = self.currency1
            self.currency1 = self.currency2
            self.currency2 = temp

        for idx in self.csv.index:
            self.csv.loc[idx, self.target] = 1 / self.csv[self.target][idx] if self.csv[self.target][idx] != 0 else 0

        self.refresh_graph()

    def reset_slider(self):
        if self.method == "Grupowanie przestrzenne":
            self.slider.setValue(50)
        if self.method == "Las izolacji":
            self.slider.setValue(20)
        if self.method == "Lokalna wartość odstająca":
            self.slider.setValue(25)

        self.refresh_graph()

    def refresh_graph(self):
        self.refresh = True
        self.update_graph()

    def reset_graph(self):
        self.checkbox.setChecked(True)
        self.init_graph()
        self.update_graph()

    def update_crosshair(self, e):
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
                self.value_label.setText(
                    "Wartość: " + str(round(self.csv[self.target][int(round(mouse_point.x()))], 7)))
