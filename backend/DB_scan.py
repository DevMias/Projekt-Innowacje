import pandas as pd
from copy import deepcopy
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler

# returning list because now we have two series


def db_scan(data1: pd.arrays, data2: pd.arrays, target: str, date: str, multiplayer=0.5) -> list:
    multiplayer = 1 - multiplayer + 0.01
    epsilon = 16 / data1.count().values[0]
    epsilon *= multiplayer

    # Check if data2 is not None (possibly important)
    if data2 is not None:
        ad_datas = [deepcopy(data1), deepcopy(data2)]
        target_cols = [ad_datas[0][[target]].copy(), ad_datas[1][[target]].copy()]
        array_length = 2
    else:
        ad_datas = [deepcopy(data1)]
        target_cols = [ad_datas[0][[target]].copy()]
        array_length = 1

    # loop to get two series of db_scan
    for i in range(0, array_length):

        scaler = StandardScaler()
        np_scaled = scaler.fit_transform(target_cols[i].values.reshape(-1, 1))
        data_scaled = pd.DataFrame(np_scaled)

        dbscan = DBSCAN(eps=epsilon, min_samples=5)

        dbscan.fit(data_scaled)
        target_cols[i]['Anomaly_after_method'] = dbscan.fit_predict(data_scaled)

        target_cols[i].loc[target_cols[i]['Anomaly_after_method'] != -1, 'Anomaly'] = False
        target_cols[i].loc[target_cols[i]['Anomaly_after_method'] == -1, 'Anomaly'] = True

        target_cols[i]['Date'] = ad_datas[i][date]
        target_cols[i] = target_cols[i].rename(columns={target: "Exchange"})

        target_cols[i] = target_cols[i].drop('Anomaly_after_method', axis=1)

        target_cols[i].insert(0, 'Date', target_cols[i].pop('Date'))
        target_cols[i].insert(1, 'Exchange', target_cols[i].pop('Exchange'))
        target_cols[i].insert(2, 'Anomaly', target_cols[i].pop('Anomaly'))

    return target_cols
