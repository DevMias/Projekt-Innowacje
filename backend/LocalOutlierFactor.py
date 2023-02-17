import numpy as np
import pandas as pd
from copy import deepcopy
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import LocalOutlierFactor


def local_outlier(datas: list = None, target: str = 'Exchange', date: str = 'Date', contamination: float = .25):
    """
            Args:
                -datas (list): List of pandas DataFrame. Each DataFrame should contain the columns "Date" and "Exchange" for the date and target variable, respectively. Default is None.
                -target (str): Name of the target variable in the DataFrame. Default is "Exchange".
                -date (str): Name of the date variable in the DataFrame. Default is "Date".
                -contamination (float): Proportion of outliers in the dataset. Default is .25.
            Returns:
                -a pandas DataFrame if only one DataFrame was passed, or a list of pandas DataFrames if multiple DataFrames were passed.
            Funcionality:
                -preprocessing data.
                -calculating anomaly score using 'LocalOutlierFactor'.
                -normalizing data using 'StandardScaler'
    """
    # PREPROCESSING: Make a single or double list depends on data2 optional parameter
    if datas is None: return
    data_list = list([ i for i in datas if i is not None ])     # delete None's from input
    if not len(data_list): return    # leave if no data
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

    return features[0] if len(features) == 1 else features
