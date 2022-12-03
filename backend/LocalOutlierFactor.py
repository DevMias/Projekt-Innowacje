import pandas as pd
from copy import deepcopy
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import LocalOutlierFactor


def local_outlier(data: pd.arrays, target: str, date: str, contamination=.25):
    neighbors = 10
    ad_data = deepcopy(data)

    features = ad_data[[target]].copy()

    scaler = StandardScaler()
    np_scaled = scaler.fit_transform(features.values.reshape(-1, 1))
    data_scaled = pd.DataFrame(np_scaled)

    neighbors = len(data) - 1 if len(data) < neighbors else neighbors

    lof = LocalOutlierFactor(n_neighbors=neighbors, contamination=contamination)
    features['Anomaly_after_method'] = lof.fit_predict(data_scaled)

    features.loc[features['Anomaly_after_method'] != -1, 'Anomaly'] = False
    features.loc[features['Anomaly_after_method'] == -1, 'Anomaly'] = True

    features['Date'] = data[date]
    features = features.rename(columns={target: "Exchange"})

    features = features.drop('Anomaly_after_method', axis=1)

    features.insert(0, 'Date', features.pop('Date'))
    features.insert(1, 'Exchange', features.pop('Exchange'))
    features.insert(2, 'Anomaly', features.pop('Anomaly'))

    return features
