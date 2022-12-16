import pandas as pd
from backend.DB_scan import db_scan
from backend.StandardDeviation import standard_deviation
from backend.IsolationForest import isolation_forest
from backend.LocalOutlierFactor import local_outlier
from backend.AutoEncoder import auto_encoder

def all_methods_combined(data: pd.arrays, target: str, date: str):
    # Run all methods and create DataFrame
    all_methods = data.copy()
    all_methods['isolation_forest'] = isolation_forest(data, target, date)['Anomaly']
    all_methods['standard_deviation'] = standard_deviation(data, target, date)['Anomaly']
    all_methods['db_scan'] = db_scan(data, target, date)['Anomaly']
    all_methods['local_outlier'] = local_outlier(data1=data, target=target, date=date)['Anomaly']
    all_methods['auto_encoder'] = auto_encoder(data, target, date)['Anomaly']

    # create new column to store anomaly values
    anomalies = list(["Anomaly_1", "Anomaly_2", "Anomaly_3", "Anomaly_4", "Anomaly_5"])

    # Fill first record with True for all anomaly
    all_methods.loc[0, anomalies] = True

    # Specify anomalies
    for x in range(1, len(all_methods.index)):
        methods_results = [all_methods['isolation_forest'][x],
                           all_methods['standard_deviation'][x],
                           all_methods['db_scan'][x],
                           all_methods['local_outlier'][x],
                           all_methods['auto_encoder'][x]]
        result_list = [False, False, False, False, False]
        result_sum = sum(methods_results) - 1
        if result_sum >= 0:
            result_list[result_sum] = True  # count number of anomalies (n) and store the result in Anomaly_n
        all_methods.loc[x, anomalies] = result_list

    # Copy only necessary data to new DataFrame
    result = pd.DataFrame(data[date])
    result['Exchange'] = all_methods[target].copy()
    result[anomalies] = all_methods[anomalies].copy()

    return result
