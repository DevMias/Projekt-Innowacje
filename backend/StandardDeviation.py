import pandas as pd
from copy import deepcopy
import numpy as np


def standard_deviation(data: pd.arrays, target: str, date: str) -> pd.arrays:
    """
    It takes in a dataframe, a target column, and a date column, and returns a dataframe with the target column, date
    column, and a new column called "Anomaly" which is a boolean value that is True if the value in the target column is
    outside of one standard deviation of the mean of the target column

    :param data: the dataframe you want to analyze
    :type data: pd.arrays
    :param target: The column name of the data you want to analyze
    :type target: str
    :param date: the date column in the dataframe
    :type date: str
    :return: A dataframe with the date, exchange, and anomaly columns.
    """
    ad_data = deepcopy(data)
    target_col = ad_data[[target]].copy()

    mean = np.mean(target_col[target])
    sd = np.std(target_col[target])

    temp_anomalies = []

    for idx, x in enumerate(target_col[target]):
        if x < mean - sd or x > mean + sd:
            temp_anomalies.append(True)
        else:
            temp_anomalies.append(False)

    target_col['Anomaly'] = temp_anomalies
    target_col['Date'] = data[date]
    target_col = target_col.rename(columns={target: "Exchange"})

    target_col.insert(0, 'Date', target_col.pop('Date'))
    target_col.insert(1, 'Exchange', target_col.pop('Exchange'))
    target_col.insert(2, 'Anomaly', target_col.pop('Anomaly'))

    return target_col
