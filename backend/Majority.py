import pandas as pd
from backend.DB_scan import db_scan
from backend.IsolationForest import isolation_forest
from backend.LocalOutlierFactor import local_outlier
from backend.StandardDeviation import standard_deviation
from backend.AutoEncoder import auto_encoder


def majority(datas: list = None, target: str = None, date: str = None):

    if datas is None:
        return
    data_list = list([i for i in datas if i is not None])  # delete None's from input
    if not len(data_list):
        return pd.DataFrame()  # leave if no data
    all_methods = list([data[[date, target]].copy() for data in data_list])

    results = list()

    for i in range(len(all_methods)):
        all_methods[i]['isolation_forest'] = isolation_forest(data_list[i], target, date)['Anomaly']
        all_methods[i]['standard_deviation'] = standard_deviation(data_list[i], target, date)['Anomaly']
        all_methods[i]['db_scan'] = db_scan(data_list[i], target, date)['Anomaly']
        all_methods[i]['local_outlier'] = local_outlier(data_list[i], target, date)['Anomaly']
        all_methods[i]['auto_encoder'] = auto_encoder(data_list[i], target, date)['Anomaly']

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

        result = pd.DataFrame(data_list[i][date])
        result['Exchange'] = all_methods[i][target].copy()
        result['Anomaly'] = all_methods[i]['Anomaly'].copy()
        results.append(result)

    return results[0] if len(results) == 1 else results
