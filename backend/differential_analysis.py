import pandas as pd
from copy import deepcopy
from sklearn.preprocessing import MinMaxScaler
from backend.backend_functions import run_method


def differential_analysis(datas: list, target: str = None, method: str = None, date: str = None, parameter=0):
    if datas is None:
        return

    ad_datas = list([deepcopy(i) for i in datas if i is not None])

    if len(ad_datas) < 2:
        return

    targets_test = list([data[[target]].copy() for data in ad_datas])

    differ = pd.DataFrame()
    differ[date] = ad_datas[0][date]

    scaler = MinMaxScaler(feature_range=(-1, 1))
    d1 = scaler.fit_transform(targets_test[0][[target]])
    d2 = scaler.fit_transform(targets_test[1][[target]])

    differ[target] = d1 - d2
    difference = run_method([differ], target, date, method, parameter)

    return difference


def get_anomalies(datas: list, target: str = None, method: str = None, date: str = None, parameter=0):
    ad_datas = list([deepcopy(i) for i in datas if i is not None])

    if len(ad_datas) < 2:
        return

    targets_cols = list([data[[date, target]].copy() for data in ad_datas])

    analysis = differential_analysis(ad_datas, target, method, date, parameter)

    for i in range(len(targets_cols)):
        targets_cols[i]['Anomaly'] = analysis.Anomaly
        targets_cols[i].rename(columns={date: "Date"}, inplace=True)
        targets_cols[i].rename(columns={target: "Exchange"}, inplace=True)

    return targets_cols
