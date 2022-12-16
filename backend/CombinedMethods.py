import pandas as pd
from backend.DB_scan import db_scan
from backend.StandardDeviation import standard_deviation
from backend.IsolationForest import isolation_forest
from backend.LocalOutlierFactor import local_outlier
from backend.AutoEncoder import auto_encoder

def all_methods_combined(data1: pd.arrays = None, data2: pd.arrays = None, target: str = 'Exchange', date: str = 'Date'):
    # Run all methods and create DataFrame
    #data2 = data.copy()

    input = list([data1, data2])  # take both to one list
    data_list = list([i for i in input if i is not None])  # delete None's from input
    if not len(data_list): return pd.DataFrame()  # leave if no data
    all_methods = list([data[[date, target]].copy() for data in data_list])  # copy date and target columns

    results = list()

    for i in range(len(all_methods)):
        all_methods[i]['isolation_forest'] = isolation_forest(data_list[i], target, date)['Anomaly']
        all_methods[i]['standard_deviation'] = standard_deviation(data_list[i], target, date)['Anomaly']
        all_methods[i]['db_scan'] = db_scan(data_list[i], target, date)['Anomaly']
        all_methods[i]['local_outlier'] = local_outlier(data1=data_list[i], target=target, date=date)['Anomaly']
        all_methods[i]['auto_encoder'] = auto_encoder(data_list[i], target, date)['Anomaly']

        # create new column to store anomaly values
        anomalies = list(["Anomaly_1", "Anomaly_2", "Anomaly_3", "Anomaly_4", "Anomaly_5"])

        # Fill first record with True for all anomaly
        all_methods[i].loc[0, anomalies] = True

        # Specify anomalies
        for x in range(1, len(all_methods[i].index)):
            methods_results = [all_methods[i]['isolation_forest'][x],
                               all_methods[i]['standard_deviation'][x],
                               all_methods[i]['db_scan'][x],
                               all_methods[i]['local_outlier'][x],
                               all_methods[i]['auto_encoder'][x]]
            result_list = [False, False, False, False, False]
            result_sum = sum(methods_results) - 1
            if result_sum >= 0:
                result_list[result_sum] = True  # count number of anomalies (n) and store the result in Anomaly_n
            all_methods[i].loc[x, anomalies] = result_list

        # Copy only necessary data to new DataFrame
        result = pd.DataFrame(data_list[i][date])
        result['Exchange'] = all_methods[i][target].copy()
        result[anomalies] = all_methods[i][anomalies].copy()

        results.append(result)

    if len(results) == 1:
        return results[0]
    return results
