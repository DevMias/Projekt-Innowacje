import pandas as pd
from copy import deepcopy
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler


# returning list because now we have two series


def db_scan(datas: list = None, target: str = None, date: str = None, multiplayer=0.5):
    if datas is None:
        return

    ad_datas = list([deepcopy(i) for i in datas if i is not None])

    if not len(ad_datas):
        return

    target_cols = list([data[[date, target]].copy() for data in ad_datas])

    multiplayer = 1 - multiplayer + 0.01
    epsilon = 16 / ad_datas[0].count().values[0]
    epsilon *= multiplayer

    # loop to get two series of db_scan
    for i in range(len(target_cols)):
        scaler = StandardScaler()
        np_scaled = scaler.fit_transform(target_cols[i][target].values.reshape(-1, 1))
        data_scaled = pd.DataFrame(np_scaled)

        dbscan = DBSCAN(eps=epsilon, min_samples=5)

        dbscan.fit(data_scaled)
        temp = dict({'Anomaly_after_method': dbscan.fit_predict(data_scaled)})

        target_cols[i].loc[temp['Anomaly_after_method'] != -1, 'Anomaly'] = False
        target_cols[i].loc[temp['Anomaly_after_method'] == -1, 'Anomaly'] = True

        target_cols[i].rename(columns={date: "Date"}, inplace=True)
        target_cols[i].rename(columns={target: "Exchange"}, inplace=True)

    return target_cols[0] if len(target_cols) == 1 else target_cols
