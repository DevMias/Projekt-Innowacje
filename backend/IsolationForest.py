import pandas as pd
from copy import deepcopy
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import IsolationForest

# returning list because now we have two series


def isolation_forest(datas: list, target: str, date: str, contamination=0.2):
    """
            Args:
                -datas (list): List of pandas DataFrame. Each DataFrame should contain the columns "Date" and "Exchange" for the date and target variable, respectively.
                -target (str): Name of the target variable in the DataFrame.
                -date (str): Name of the date variable in the DataFrame.
                -contamination (float): Proportion of outliers in the dataset. Default is 0.2.
            Returns:
                -pandas dataframe single or a list depending on number of inputs with each having additional column 'Anomaly'
            Funcionality:
                -implementing isolation_forest alghoritm used for outlier detection:
                -normalizing using 'StandardScaler'
                -applying isolation_forest alghoritm
                -adding new column "Anoamly'
    """
    if datas is None:
        return

    ad_datas = list([deepcopy(i) for i in datas if i is not None])

    if not len(ad_datas):
        return

    target_cols = list([data[[date, target]].copy() for data in ad_datas])

    # loop to get two series of isolation forest
    for i in range(len(target_cols)):

        scaler = StandardScaler()
        np_scaled = scaler.fit_transform(target_cols[i][target].values.reshape(-1, 1))
        data_scaled = pd.DataFrame(np_scaled)

        forest = IsolationForest(n_estimators=100, contamination=contamination)

        forest.fit(data_scaled)
        temp = dict({'Anomaly_after_method': forest.fit_predict(data_scaled)})

        target_cols[i].loc[temp['Anomaly_after_method'] != -1, 'Anomaly'] = False
        target_cols[i].loc[temp['Anomaly_after_method'] == -1, 'Anomaly'] = True

        target_cols[i].rename(columns={date: "Date"}, inplace=True)
        target_cols[i].rename(columns={target: "Exchange"}, inplace=True)

    return target_cols[0] if len(target_cols) == 1 else target_cols
