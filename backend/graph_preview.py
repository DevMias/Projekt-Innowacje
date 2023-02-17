import pyqtgraph as pg

from backend import backend_functions


def create_plot(graph, plot_info):
    """
            Args:
                -graph PlotWidget object
                -plot_info dictionary containing information about a plot that will be created
            Returns:
                -PlotWidget object displaying plot of currency exchange rate data.
            Funcionality"
                -creating plot widget and shows data of a currency exchange.
    """
    if graph is None:
        graph = pg.PlotWidget()

    graph.setBackground('w')

    if plot_info["title"].text() == "":
        graph.setTitle(plot_info["currencies"][0].currentText()[:3] + '/' + plot_info["currencies"][1].currentText()[:3])
    else:
        graph.setTitle(plot_info["title"].text())

    link = backend_functions.create_link([plot_info["currencies"][0].currentText()[:3],
                                         plot_info["currencies"][1].currentText()[:3]],
                                         backend_functions.return_date(plot_info["dates"][0]),
                                         backend_functions.return_date(plot_info["dates"][1]),
                                         plot_info["interval"].currentText())
    csv = backend_functions.download_csv_without_errors(link[0])

    graph.clear()

    if csv is None:
        graph.setTitle("Błąd")
        graph.showGrid(x=False, y=False, alpha=1.0)
        graph.setXRange(0, 0)
        graph.setYRange(0, 0)
        x_axis = graph.getAxis("bottom")
        x_ticks_dict = {0: "Błąd"}
        x_axis.setTicks([x_ticks_dict.items()])
        y_axis = graph.getAxis("left")
        y_axis.setTicks([x_ticks_dict.items()])
        return graph

    graph.setXRange(0, len(csv["Data"]))
    graph.setYRange(min(csv["Zamkniecie"]), max(csv["Zamkniecie"]))

    mult = len(csv["Data"]) // 9 if len(csv["Data"]) > 9 else 1
    x_ticks_dict = {}
    for i in range(0, len(csv["Data"]) // mult + 1):
        if i * mult < len(csv["Data"]):
            x_ticks_dict[i * mult] = csv["Data"][i * mult]

    x_ticks = x_ticks_dict.items()

    x_axis = graph.getAxis("bottom")
    x_axis.setTicks([x_ticks])

    y_axis = graph.getAxis("left")
    y_axis.setTicks(None)

    graph.plot(csv.index, csv["Zamkniecie"], pen=pg.mkPen("b", width=2))

    graph.showGrid(x=True, y=False, alpha=1.0)

    graph.setMouseEnabled(x=False, y=False)

    return graph
