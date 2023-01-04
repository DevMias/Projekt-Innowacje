import pandas as pd
from copy import deepcopy
import numpy as np


def standard_deviation(datas: list, target: str, date: str) -> pd.arrays:
    
    if datas is None:
        return
    
    ad_datas = list([deepcopy(i) for i in datas if i is not None])

    if len(ad_datas) == 0:
        return


    target_cols = list([data[[date, target]].copy() for data in ad_datas])

    means = []
    sds = []
    for target_col in target_cols:
        means.append(np.mean(target_col[target]))
        sds.append(np.std(target_col[target]))

    temp_anomalies = [[] for _ in range(target_cols[target])]

    for i, target_col in enumerate(target_cols[target]):
        if target_col < means[i] - sds[i] or target_col > means[i] + sds[i]:
            temp_anomalies[i].append(True)
        else:
            temp_anomalies[i].append(False)

    target_col['Anomaly'] = temp_anomalies
    target_col['Date'] = data[date]
    target_col = target_col.rename(columns={target: "Exchange"})

    target_cols[i].rename(columns={date: "Date"}, inplace=True)
    target_cols[i].rename(columns={target: "Exchange"}, inplace=True)
    target_col.insert(2, 'Anomaly', target_col.pop('Anomaly'))

  
    if len(target_cols) == 1:
        return target_cols[0]
    else:
        return target_cols
