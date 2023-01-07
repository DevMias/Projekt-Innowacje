import numpy as np
import pandas as pd
import tensorflow as tf
from copy import deepcopy
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras import Model, Sequential
from tensorflow.keras.layers import Dense, Dropout
from sklearn.model_selection import train_test_split


def auto_encoder(datas: list = None, target: str = None, date: str = None, split_perc=0.5):
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
    reconstructions = model.predict(x_train_scaled)
    # provides losses of individual instances

    reconstruction_errors = tf.keras.losses.msle(reconstructions, x_train_scaled)
    # threshold for anomaly scores

    threshold = np.mean(reconstruction_errors.numpy()) + np.std(reconstruction_errors.numpy())
    return threshold


def get_predictions(model, x_test_scaled, threshold):
    predictions = model.predict(x_test_scaled)
    # provides losses of individual instances

    errors = tf.keras.losses.msle(predictions, x_test_scaled)
    # 0 = anomaly, 1 = normal

    anomaly_mask = pd.Series(errors) > threshold

    preds = anomaly_mask.map(lambda x: 0.0 if x is True else 1.0)

    return preds
