import numpy as np
import pandas as pd
from copy import deepcopy
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import LocalOutlierFactor


def local_outlier(data1: pd.arrays = None, data2: pd.array = None, target: str = 'Exchange', date: str = 'Date', contamination: float = .25, ) -> pd.DataFrame:
    #return local_outlier_differential_analysis(data, target, date, contamination=.25)

    # test case: data2 != None
    #data2 = data1.copy()
    #data1 = None

    # PREPROCESSING: Make a single or double list depends on data2 optional parameter
    input = list([ data1, data2 ])  # take both to one list
    data_list = list([ i for i in input if i is not None ])     # delete None's from input
    if not len(data_list): return pd.DataFrame()    # leave if no data
    features = list([ data[[ date, target ]].copy() for data in data_list ])  # copy date and target columns

    # CALCULATION: Iterate by the lists
    neighbors = 10
    for i in range(len(data_list)):
        # Normalization
        scaler = StandardScaler()
        np_scaled = scaler.fit_transform(features[i][target].values.reshape(-1, 1))
        data_scaled = pd.DataFrame(np_scaled)

        # setting parameter and start calculations
        neighbors = len(data_list[i]) - 1 if len(data_list[i]) < neighbors else neighbors
        lof = LocalOutlierFactor(n_neighbors=neighbors, contamination=contamination)
        temp = dict({ 'Anomaly_after_method': lof.fit_predict(data_scaled) })

        # change to true/false
        features[i].loc[temp['Anomaly_after_method'] != -1, 'Anomaly'] = False
        features[i].loc[temp['Anomaly_after_method'] == -1, 'Anomaly'] = True

        # Rename columns in case different names from parameter
        features[i].rename(columns={date: "Date"}, inplace=True)
        features[i].rename(columns={target: "Exchange"}, inplace=True)

    # POSTPROCESSING:
    if data2 is None:
        print(features[0])
        return features[0]   # output like: df(Date, Exchange, Anomaly)
    else:
        result = pd.DataFrame(features[0]['Date'])
        for i in range(len(features)):
            result['Exchange_'+str(i+1)] = features[i]['Exchange']
            result['Anomaly_'+str(i+1)] = features[i]['Anomaly']
        print(result)
        return result   # output like: df(Date, Exchange_1, Anomaly_1, Exchange_2, Anomaly_2)
