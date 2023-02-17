import pandas as pd
from copy import deepcopy
import numpy as np


def standard_deviation(datas: list = None, target: str = None, date: str = None):
    """
            Args:
                -datas: a list of dataframes containing target variable data
                -target: the name of the target variable
                -date: the name of the date column
            Returns:
                -None if dataframes in 'datas' ate all None
            Functionality:
                -calculating standard deviation.
                - identifying anomalies
           """
    if datas is None:
        return

    ad_datas = list([deepcopy(i) for i in datas if i is not None])

    if not len(ad_datas):
        return

    target_cols = list([data[[date, target]].copy() for data in ad_datas])

    for i in range(len(target_cols)):
        mean = np.mean(target_cols[i][target])
        sd = np.std(target_cols[i][target])

        temp_anomalies = []

        for idx, x in enumerate(target_cols[i][target]):
            if x < mean - sd or x > mean + sd:
                temp_anomalies.append(True)
            else:
                temp_anomalies.append(False)

        target_cols[i]['Anomaly'] = temp_anomalies
        target_cols[i].rename(columns={date: "Date"}, inplace=True)
        target_cols[i].rename(columns={target: "Exchange"}, inplace=True)

    return target_cols[0] if len(target_cols) == 1 else target_cols