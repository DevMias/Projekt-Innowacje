import pandas as pd
from backend.DB_scan import db_scan
from backend.StandardDeviation import standard_deviation
from backend.IsolationForest import isolation_forest
from backend.LocalOutlierFactor import local_outlier
from backend.AutoEncoder import auto_encoder


def all_methods_combined(data: pd.arrays, target: str, date: str):
    """
    It takes the results of each method and combines them into one dataframe

    :param data: the dataframe that contains the data
    :type data: pd.arrays
    :param target: the column name of the target variable
    :type target: str
    :param date: the date column in the dataframe
    :type date: str
    :return: A dataframe with the date, exchange, and the anomaly results for each method.
    """
    all_methods = data.copy()
    all_methods['isolation_forest'] = isolation_forest(data, target, date)['Anomaly']
    all_methods['standard_deviation'] = standard_deviation(data, target, date)['Anomaly']
    all_methods['db_scan'] = db_scan(data, target, date)['Anomaly']
    all_methods['local_outlier'] = local_outlier(data, target, date)['Anomaly']
    all_methods['auto_encoder'] = auto_encoder(data, target, date)['Anomaly']

    all_methods = all_methods.assign(Anomaly_1=False)
    all_methods = all_methods.assign(Anomaly_2=False)
    all_methods = all_methods.assign(Anomaly_3=False)
    all_methods = all_methods.assign(Anomaly_4=False)
    all_methods = all_methods.assign(Anomaly_5=False)
    for x in range(all_methods.index.min(), all_methods.index.max()):
        counter = 0

        methods_results = [all_methods['isolation_forest'][x], all_methods['standard_deviation'][x],
                           all_methods['db_scan'][x], all_methods['local_outlier'][x], all_methods['auto_encoder'][x]]

        for result in methods_results:
            if result:
                counter += 1

        # TODO simplify by using loops
        if counter == 1:
            all_methods.loc[x, 'Anomaly_1'] = True
        if counter == 2:
            all_methods.loc[x, 'Anomaly_2'] = True
        if counter == 3:
            all_methods.loc[x, 'Anomaly_3'] = True
        if counter == 4:
            all_methods.loc[x, 'Anomaly_4'] = True
        if counter == 5:
            all_methods.loc[x, 'Anomaly_5'] = True

    idx = all_methods.index.min()

    all_methods.loc[idx, 'Anomaly_1'] = True
    all_methods.loc[idx, 'Anomaly_2'] = True
    all_methods.loc[idx, 'Anomaly_3'] = True
    all_methods.loc[idx, 'Anomaly_4'] = True
    all_methods.loc[idx, 'Anomaly_5'] = True

    result = pd.DataFrame(data[date])
    result['Exchange'] = all_methods[target].copy()
    result['Anomaly_1'] = all_methods['Anomaly_1'].copy()
    result['Anomaly_2'] = all_methods['Anomaly_2'].copy()
    result['Anomaly_3'] = all_methods['Anomaly_3'].copy()
    result['Anomaly_4'] = all_methods['Anomaly_4'].copy()
    result['Anomaly_5'] = all_methods['Anomaly_5'].copy()

    result.insert(0, 'Date', result.pop('Date'))
    result.insert(1, 'Exchange', result.pop('Exchange'))
    result.insert(2, 'Anomaly_1', result.pop('Anomaly_1'))
    result.insert(3, 'Anomaly_2', result.pop('Anomaly_2'))
    result.insert(4, 'Anomaly_3', result.pop('Anomaly_3'))
    result.insert(5, 'Anomaly_4', result.pop('Anomaly_4'))
    result.insert(6, 'Anomaly_5', result.pop('Anomaly_5'))

    return result
