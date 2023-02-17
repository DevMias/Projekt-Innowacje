import numpy as np
import pandas as pd
import tensorflow as tf
from copy import deepcopy
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras import Model, Sequential
from tensorflow.keras.layers import Dense, Dropout
from sklearn.model_selection import train_test_split


def auto_encoder(datas: list = None, target: str = None, date: str = None, split_perc=0.5):
    """
        Args:
            -datas: list, default=None - A list of pandas dataframes containing the data.
            -target: str, default=None - A string representing the column name of the target variable.
            -date: str, default=None - A string representing the column name of the date variable.
            -split_perc: float, default=0.5 - A float representing the proportion of the dataset to include in the test split.
        Returns:

            -target_cols[0] if len(target_cols) == 1 else target_cols: A pandas dataframe representing the data with the anomaly detection result column.

        Functionality:
            -function is an implementation of the Autoencoder anomaly detection method.
            The function takes a list of dataframes, target column name, date column name, and split percentage as inputs.
            The function then trains an autoencoder model on the data with the use of novelty detection.
            The function returns a dataframe that shows anomalies in the data.
            The function first creates a copy of the data in the input dataframe and checks if it is not empty.
            Then it creates a list of target columns by selecting the date and target columns from the data.
            It then goes through each target column in the list and performs the following steps:
                    -selects the target column and creates a copy of it.
                    -splits the data into training and testing datasets.
                    -uses the training dataset to train the autoencoder model using the selected novelty detection method.
                    -predicts and finds the threshold for anomaly detection based on the testing data using the trained model.
                    -predicts the anomalies in the data using the threshold, and returns a copy of the original data with an additional column called "Anomaly" that flags the data as an anomaly or not.
        """
    if datas is None:
        return

    ad_datas = list([deepcopy(i) for i in datas if i is not None])

    if not len(ad_datas):
        return

    target_cols = list([data[[date, target]].copy() for data in ad_datas])

    for i in range(len(target_cols)):
        features = ad_datas[i][[target]].copy()
        target_data = ad_datas[i][[target]].copy()

        x_train, x_test, y_train, y_test = train_test_split(
            features, target_data, test_size=split_perc
        )

        # use case is novelty detection so use only the normal data
        # for training
        train_index = y_train[y_train == 1].index
        train_data = x_train.loc[train_index]

        # min max scale the input data
        min_max_scaler = MinMaxScaler(feature_range=(0, 1))
        x_train_scaled = min_max_scaler.fit_transform(train_data.copy())
        x_test_scaled = min_max_scaler.transform(features.copy())

        class AutoEncoder(Model):

            def __init__(self, output_units, code_size=8):
                super().__init__()
                self.encoder = Sequential([
                    Dense(64, activation='relu'),
                    Dropout(0.1),
                    Dense(32, activation='relu'),
                    Dropout(0.1),
                    Dense(16, activation='relu'),
                    Dropout(0.1),
                    Dense(code_size, activation='relu')
                ])
                self.decoder = Sequential([
                    Dense(16, activation='relu'),
                    Dropout(0.1),
                    Dense(32, activation='relu'),
                    Dropout(0.1),
                    Dense(64, activation='relu'),
                    Dropout(0.1),
                    Dense(output_units, activation='sigmoid')
                ])

            def call(self, inputs):
                encoded = self.encoder(inputs)
                decoded = self.decoder(encoded)
                return decoded

        model = AutoEncoder(output_units=x_train_scaled.shape[1])
        # configurations of model
        model.compile(loss='msle', metrics=['mse'], optimizer='adam')

        threshold = find_threshold(model, x_train_scaled)
        predictions = get_predictions(model, x_test_scaled, threshold)

        temp = dict({'Anomaly_after_method': predictions.copy()})

        target_cols[i].loc[temp['Anomaly_after_method'] != 1, 'Anomaly'] = True
        target_cols[i].loc[temp['Anomaly_after_method'] == 1, 'Anomaly'] = False

        target_cols[i].rename(columns={date: "Date"}, inplace=True)
        target_cols[i].rename(columns={target: "Exchange"}, inplace=True)

        idx = target_cols[i].index.min()

        target_cols[i].loc[idx, 'Anomaly'] = True

    return target_cols[0] if len(target_cols) == 1 else target_cols


def find_threshold(model, x_train_scaled):
    """
        Args:
            -model: a trained autoencoder model.
            -x_train_scaled: scaled training data used to train the model.
        Returns:
            -threshold: threshold for anomaly scores.
        Functionality:
            -The find_threshold function takes a trained autoencoder model and scaled training data as inputs.
            It uses the model to generate reconstructions of the training data and calculates the mean and standard deviation of the mean squared logarithmic error (MSLE) of the reconstructions.
    """
    reconstructions = model.predict(x_train_scaled)
    # provides losses of individual instances

    reconstruction_errors = tf.keras.losses.msle(reconstructions, x_train_scaled)
    # threshold for anomaly scores

    threshold = np.mean(reconstruction_errors.numpy()) + np.std(reconstruction_errors.numpy())
    return threshold


def get_predictions(model, x_test_scaled, threshold):
    """
        Args:
            -model: A trained Autoencoder model from the TensorFlow Keras library
            -x_test_scaled: A numpy array with shape (n_samples, n_features) containing the scaled test data
            -threshold: A float representing the threshold for distinguishing anomalies from normal data.

        Returns:
            -preds: A pandas Series containing the predicted labels for each instance in the test set. A value of 0 indicates an anomaly, and a value of 1 indicates normal data.

        Functionality:
            -function takes a trained autoencoder model, a set of scaled test data, and a threshold value.
            It generates predictions for the test data based on the trained model and then determines if each instance is an anomaly or not based on the provided threshold.
            Anomalies are assigned a value of 0 and normal data are assigned a value of 1, and the function returns these values as a Pandas series.
    """
    predictions = model.predict(x_test_scaled)
    # provides losses of individual instances

    errors = tf.keras.losses.msle(predictions, x_test_scaled)
    # 0 = anomaly, 1 = normal

    anomaly_mask = pd.Series(errors) > threshold

    preds = anomaly_mask.map(lambda x: 0.0 if x is True else 1.0)

    return preds
