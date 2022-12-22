import pandas as pd
from backend.DB_scan import db_scan
from backend.IsolationForest import isolation_forest
from backend.LocalOutlierFactor import local_outlier
from backend.StandardDeviation import standard_deviation
from backend.AutoEncoder import auto_encoder


def majority(data: pd.arrays, target: str, date: str):
    all_methods = data.copy()
    all_methods['isolation_forest'] = isolation_forest(data, target, date)['Anomaly']
    all_methods['standard_deviation'] = standard_deviation(data, target, date)['Anomaly']
    all_methods['db_scan'] = db_scan(data, target, date)['Anomaly']
    all_methods['local_outlier'] = local_outlier(datas=[data], target=target, date=date)['Anomaly']
    all_methods['auto_encoder'] = auto_encoder(data, target, date)['Anomaly']

    all_methods = all_methods.assign(Anomaly=False)
    for x in range(all_methods.index.min(), all_methods.index.max()):
        counter = 0
        number_of_methods = 5

        methods_results = [all_methods['isolation_forest'][x], all_methods['standard_deviation'][x],
                           all_methods['db_scan'][x], all_methods['local_outlier'][x], all_methods['auto_encoder'][x]]

        for result in methods_results:
            if result:
                counter += 1

        if counter / number_of_methods >= 0.5:
            all_methods.loc[x, 'Anomaly'] = True

    result = pd.DataFrame(data[date])
    result['Exchange'] = all_methods[target].copy()
    result['Anomaly'] = all_methods['Anomaly'].copy()

    result.insert(0, 'Date', result.pop('Date'))
    result.insert(1, 'Exchange', result.pop('Exchange'))
    result.insert(2, 'Anomaly', result.pop('Anomaly'))

    return result
