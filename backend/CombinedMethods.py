import pandas as pd
from backend.DB_scan import db_scan
from backend.StandardDeviation import standard_deviation
from backend.IsolationForest import isolation_forest
from backend.LocalOutlierFactor import local_outlier
from backend.AutoEncoder import auto_encoder
from front.styles import method_properties as mp

def all_methods_combined(datas: list = None, target: str = 'Exchange', date: str = 'Date'):
    """
            Args:
                -datas (list of pandas dataframes): A list of pandas dataframes, where each dataframe contains a time series with two
                -columns: 'date' and 'target' (value of the time series at that date).
                -target (str): The name of the column in the input dataframes that contains the target values (time series values). Thedefault value is 'Exchange'.
                -date (str): The name of the column in the input dataframes that contains the date values. The default value is 'Date'.

            Returns:
                   Union[pd.DataFrame, List[pd.DataFrame]]: Returns either a single pandas dataframe or a list of pandas dataframes,
                   depending on the length of the input list. Each returned dataframe has multiple additional columns, one for each
                   of the five methods and one for each possible combination of methods (up to five anomalies), that indicate whether
                   a data point in the time series is an anomaly or not, as identified by the respective method(s).

            Funcionality:
                   Applying a combination of five anomaly detection methods (Isolation Forest, Standard Deviation, DBSCAN, Local
                   Outlier Factor, and Autoencoder) to identify anomalies in a given time series data. It takes in a list of pandas dataframes
                   as input, where each dataframe contains a time series with two columns: 'date' and 'target' (value of the time series at
                   that date). The function returns a list of pandas dataframes, where each dataframe has multiple additional columns,
                   one for each of the five methods and one for each possible combination of methods (up to five anomalies), that indicate
                   whether a data point in the time series is an anomaly or not, as identified by the respective method(s).
    """
    # Run all methods and create DataFrame
    if datas is None: return
    data_list = list([i for i in datas if i is not None])  # delete None's from input
    if not len(data_list): return pd.DataFrame()  # leave if no data
    all_methods = list([data[[date, target]].copy() for data in data_list])  # copy date and target columns

    results = list()

    name = [key for key in mp.keys()]   # method names connected to styles (front.style.py)
    for i in range(len(all_methods)):
        all_methods[i][name[0]] = isolation_forest(datas=[data_list[i]], target=target, date=date)['Anomaly']
        all_methods[i][name[1]] = standard_deviation(datas=[data_list[i]], target=target, date=date)['Anomaly']
        all_methods[i][name[2]] = db_scan(datas=[data_list[i]], target=target, date=date)['Anomaly']
        all_methods[i][name[3]] = local_outlier(datas=[data_list[i]], target=target, date=date)['Anomaly']
        all_methods[i][name[4]] = auto_encoder(datas=[data_list[i]], target=target, date=date)['Anomaly']

        # create new column to store anomaly values
        anomalies = list(["Anomaly_1", "Anomaly_2", "Anomaly_3", "Anomaly_4", "Anomaly_5"])

        # Fill first record with True for all anomaly
        all_methods[i].loc[0, anomalies] = True

        # Specify anomalies
        for x in range(1, len(all_methods[i].index)):
            methods_results = [all_methods[i][name[0]][x],
                               all_methods[i][name[1]][x],
                               all_methods[i][name[2]][x],
                               all_methods[i][name[3]][x],
                               all_methods[i][name[4]][x]]
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

    return results[0] if len(results) == 1 else results
