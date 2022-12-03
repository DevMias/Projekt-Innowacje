import pandas as pd
from copy import deepcopy
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import IsolationForest


def isolation_forest(data: pd.arrays, target: str, date: str, contamination=0.2):
    ad_data = deepcopy(data)

    target_col = ad_data[[target]].copy()

    scaler = StandardScaler()
    np_scaled = scaler.fit_transform(target_col.values.reshape(-1, 1))
    data_scaled = pd.DataFrame(np_scaled)

    forest = IsolationForest(n_estimators=100, contamination=contamination)

    forest.fit(data_scaled)
    target_col['Anomaly_after_method'] = forest.fit_predict(data_scaled)

    target_col.loc[target_col['Anomaly_after_method'] != -1, 'Anomaly'] = False
    target_col.loc[target_col['Anomaly_after_method'] == -1, 'Anomaly'] = True

    target_col['Date'] = data[date]
    target_col = target_col.rename(columns={target: "Exchange"})

    target_col = target_col.drop('Anomaly_after_method', axis=1)

    target_col.insert(0, 'Date', target_col.pop('Date'))
    target_col.insert(1, 'Exchange', target_col.pop('Exchange'))
    target_col.insert(2, 'Anomaly', target_col.pop('Anomaly'))

    return target_col
