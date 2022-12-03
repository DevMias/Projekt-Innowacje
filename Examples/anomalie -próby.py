# -*- coding: utf-8 -*-
"""
Created on Fri Feb 25 15:39:14 2022

@author: adamp
"""

import pandas as pd
#s = pd.read_csv("D:/PythonWorkspace/do zajęć/temperature.csv", index_col="Time", parse_dates=True, squeeze=True)
from adtk.data import validate_series
import matplotlib.pyplot as plt
from datetime import datetime

from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import IsolationForest
from sklearn.svm import OneClassSVM
from sklearn.covariance import EllipticEnvelope
from sklearn.neighbors import LocalOutlierFactor
from sklearn.neighbors import KernelDensity
from numpy import quantile, where

def parser(s):
    return datetime.strptime(s, '%d/%m/%Y')

s1 = pd.read_csv("Dane historyczne dla CHF_PLN4.csv",parse_dates=[0], index_col=0, date_parser=parser)

#s1 = pd.read_csv("D:/PythonWorkspace/do zajęć/Dane historyczne dla CHF_PLN3.csv", index_col="Time", parse_dates=True,  squeeze=True)
s1 = validate_series(s1)
#print(s1)

plt.figure(figsize=(10,4))
plt.plot(s1)
plt.title('Kurs CHF/PLN', fontsize=20)
plt.ylabel('Kurs', fontsize=16)
plt.show()

#---------------------------

scaler = StandardScaler()
np_scaled = scaler.fit_transform(s1.values.reshape(-1, 1))
data = pd.DataFrame(np_scaled)



# train isolation forest
outliers_fraction = float(.05)
model =  IsolationForest(contamination=outliers_fraction)
model.fit(data) 

s1['anomaly'] = model.predict(data)

#plt.plot(s1['anomaly'])

#print(s1['anomaly'])

# visualization
fig, ax = plt.subplots(figsize=(10,6))

a = s1.loc[s1['anomaly'] == -1, ['Ostatnio']] #anomaly
#print(s1)

ax.plot(s1.index, s1['Ostatnio'], color='black', label = 'Normal')
ax.scatter(a.index,a['Ostatnio'], color='red', label = 'Anomaly')
plt.legend()
plt.show();

#-----------------------------------

model = OneClassSVM(nu=outliers_fraction, kernel="rbf", gamma=0.05)
model.fit(data)
s1['anomaly'] = model.predict(data)
#print(s1['anomaly'])
fig, ax = plt.subplots(figsize=(10,6))

a = s1.loc[s1['anomaly'] == -1, ['Ostatnio']] #anomaly

ax.plot(s1.index, s1['Ostatnio'], color='black', label = 'Normal')
ax.scatter(a.index,a['Ostatnio'], color='red', label = 'Anomaly')
plt.legend()
plt.show();

#-----------------------------------

envelope =  EllipticEnvelope(contamination = outliers_fraction) 
X_train = np_scaled
envelope.fit(X_train)
#df_class1 = pd.DataFrame(df_class1)
#s1['Ostatnio'] = envelope.decision_function(X_train)
s1['anomaly'] = envelope.predict(X_train)

#df_class = pd.concat([df_class0, df_class1])
#df['anomaly5'] = df_class['anomaly']

fig, ax = plt.subplots(figsize=(10, 6))
a = s1.loc[s1['anomaly'] == -1, ['Ostatnio']] #anomaly


ax.plot(s1.index, s1['Ostatnio'], color='black', label = 'Normal')
ax.scatter(a.index,a['Ostatnio'], color='red', label = 'Anomaly')
plt.legend()
plt.show();

#------------------------------------
model = LocalOutlierFactor(n_neighbors=20, contamination=0.05)
s1['anomaly']=model.fit_predict(data)

fig, ax = plt.subplots(figsize=(10,6))

a = s1.loc[s1['anomaly'] == -1, ['Ostatnio']] #anomaly

ax.plot(s1.index, s1['Ostatnio'], color='black', label = 'Normal')
ax.scatter(a.index,a['Ostatnio'], color='red', label = 'Anomaly')
plt.legend()
plt.show();

#---------------------------------

kern_dens = KernelDensity()
kern_dens.fit(s1)

s1['anomaly'] = kern_dens.score_samples(s1)
threshold = quantile(s1['anomaly'], .05)
print(threshold)
fig, ax = plt.subplots(figsize=(10,6))

a = s1.loc[s1['anomaly'] <= threshold, ['Ostatnio']] #anomaly
 
ax.plot(s1.index, s1['Ostatnio'], color='black', label = 'Normal')
ax.scatter(a.index,a['Ostatnio'], color='red', label = 'Anomaly')
plt.legend()
plt.show()


#---------------do sprawdzenia
#     https://www.statsmodels.org/dev/examples/index.html
#-------------------