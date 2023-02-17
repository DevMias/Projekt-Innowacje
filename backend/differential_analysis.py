import pandas as pd
from copy import deepcopy
from sklearn.preprocessing import MinMaxScaler
from backend.backend_functions import run_method


def differential_analysis(datas: list, target: str = None, method: str = None, date: str = None, parameter=0.1):
    """
            Args:
                -datas (list): A list of datasets to be analyzed.
                -target (str, optional): The target variable to analyze for anomalies. Default is set to None.
                -method (str, optional): The anomaly detection method to use. Default is set to None.
                -date (str, optional): The name of the date column in the dataset. Default is set to None.
                -parameter (float, optional): A parameter used by the specified anomaly detection method. Default is set to 0.1.
            Returns:
                -parameter (float, optional): A parameter used by the specified anomaly detection method. Default is set to 0.1.
            Funcionality:
                -creating differ dataframe with a date column and a target column, and scales the target variable for the first and second datasets using a 'MinMaxScaler', setting range.
                -calculating difference between two scaled variables and saving it in 'differ' dataframe.
                -running specified detection method.
    """
    if datas is None:
        return

    ad_datas = list([deepcopy(i) for i in datas if i is not None])

    if len(ad_datas) < 2:
        return

    targets_test = list([data[[target]].copy() for data in ad_datas])

    differ = pd.DataFrame()
    differ[date] = ad_datas[0][date]

    scaler = MinMaxScaler(feature_range=(-1, 1))
    d1 = scaler.fit_transform(targets_test[0][[target]])
    d2 = scaler.fit_transform(targets_test[1][[target]])

    differ[target] = d1 - d2
    difference = run_method([differ], target, date, method, parameter)

    return difference


def get_anomalies(datas: list, target: str = None, method: str = None, date: str = None, parameter=0.1):
    """
        Args:
            -datas (list): a list of pandas dataframes with time series data to analyze.
            -target (str): the name of the target variable to analyze, as a string. Default is None.
            -method (str): the name of the method to use for anomaly detection, as a string. Possible values are:"RobustZScore", "MedianAbsoluteDeviation", "ExtremeStudentizedDeviation", "None" or "Wszystkie". Default is None.
            -date (str): the name of the date column in the dataframes, as a string. Default is None.
            -parameter (float): a parameter used by the anomaly detection method, as a float. Default is 0.1.

        Returns:
            list: a list of pandas dataframes with the same time series data as the input dataframes, with an additional column
            "Anomaly" or "Anomaly_X" for each method used (where X is the number of the method), containing the anomaly score
            for each time point. If there are less than 2 dataframes in the input list, the function returns None.
    """
    ad_datas = list([deepcopy(i) for i in datas if i is not None])

    if len(ad_datas) < 2:
        return

    targets_cols = list([data[[date, target]].copy() for data in ad_datas])

    analysis = differential_analysis(ad_datas, target, method, date, parameter)

    for i in range(len(targets_cols)):
        if method == 'Wszystkie':
            targets_cols[i] = targets_cols[i].assign(Anomaly_1=analysis.Anomaly_1,
                                                     Anomaly_2=analysis.Anomaly_2,
                                                     Anomaly_3=analysis.Anomaly_3,
                                                     Anomaly_4=analysis.Anomaly_4,
                                                     Anomaly_5=analysis.Anomaly_5)
        else:
            targets_cols[i]['Anomaly'] = analysis.Anomaly
        targets_cols[i].rename(columns={date: "Date"}, inplace=True)
        targets_cols[i].rename(columns={target: "Exchange"}, inplace=True)

    return targets_cols
