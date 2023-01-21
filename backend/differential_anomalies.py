from copy import deepcopy

from backend.differential_analysis import differential_analysis


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