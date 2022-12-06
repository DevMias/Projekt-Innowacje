import pandas as pd
from copy import deepcopy
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import IsolationForest


def isolation_forest(data: pd.arrays, target: str, date: str, contamination=0.2):
    """
    The function takes in a dataframe, a target column, a date column, and a contamination value. It then creates a copy of
    the dataframe, and creates a new dataframe with the target column. It then scales the target column, and fits the scaled
    data to an Isolation Forest model. The model then predicts anomalies, and the function returns a dataframe with the
    date, exchange, and anomaly columns

    :param data: pd.arrays - the dataframe that contains the data you want to analyze
    :type data: pd.arrays
    :param target: The column name of the target variable
    :type target: str
    :param date: the date column in the dataframe
    :type date: str
    :param contamination: The amount of contamination of the data set, i.e. the proportion of outliers in the data set. Used
    when fitting to define the threshold on the decision function
    :return: A dataframe with the date, exchange, and anomaly columns.
    """
    ad_data = deepcopy(data)

    target_col = ad_data[[target]].copy()

    scaler = StandardScaler()
    np_scaled = scaler.fit_transform(target_col.values.reshape(-1, 1))
    data_scaled = pd.DataFrame(np_scaled)

    forest = IsolationForest(n_estimators=100, contamination=contamination)

    forest.fit(data_scaled)
    target_col['Anomaly_after_method'] = forest.fit_predict(data_scaled)

    target_col.loc[target_col['Anomaly_after_method'] != -1, 'Anomaly'] = False
    target_col.loc[target_col['Anomaly_after_method'] == -1, 'Anomaly'] = True

    target_col['Date'] = data[date]
    target_col = target_col.rename(columns={target: "Exchange"})

    target_col = target_col.drop('Anomaly_after_method', axis=1)

    target_col.insert(0, 'Date', target_col.pop('Date'))
    target_col.insert(1, 'Exchange', target_col.pop('Exchange'))
    target_col.insert(2, 'Anomaly', target_col.pop('Anomaly'))

    return target_col
