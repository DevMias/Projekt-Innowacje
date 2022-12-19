import pandas as pd
from copy import deepcopy
from sklearn.preprocessing import MinMaxScaler
from backend.backend_functions import run_method


# differential analysis (to check)


def differential_analysis(data1: pd.arrays = None, data2: pd.arrays = None, target: str = None, method: str = None,
                          date: str = None, parameter=0):
    ad_datas = [deepcopy(data1), deepcopy(data2)]
    targets_test = [ad_datas[0][[target]].copy(), ad_datas[1][[target]].copy()]
    differ = pd.DataFrame()
    differ["Data"] = ad_datas[0][date]

    scaler = MinMaxScaler(feature_range=(-1, 1))
    d1 = scaler.fit_transform(targets_test[0][[target]])
    d2 = scaler.fit_transform(targets_test[1][[target]])

    differ[target] = d1 - d2
    difference = run_method(differ, target, date, method, parameter)

    return difference
