# -*- coding: utf-8 -*-
"""Machine Learning Red LSTM_COP/USD

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1k_PYak0VbhvqeiVDyyPC_vTXupWGuugd
"""

#librerias
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import datetime
##### REPRODUCIBILIDAD
import tensorflow as tf
import keras
import numpy as np
tf.random.set_seed(20) #semilla para reproduccion
np.random.seed(20)     #semilla para reproduccion

#CARGAMOS LOS DATOS
dataset1 = pd.read_csv('COP=X_TRAINING.csv', index_col='Date', parse_dates=True)
dataset1.head()
#dataset1.shape

#LIMPIAMOS LOS DATOS
dataset = dataset1.dropna()
dataset.isna().any()

dataset.info()

dataset['Close'].plot(figsize=(16,6))

#se definen los datos de entrenamiento (van desde el 19 de febrero de 2019 hasta el 31 de diciembre de 2020)
training_set=dataset['Close']
training_set=pd.DataFrame(training_set)

#Escalamiento ya que LSTM es sensible a la escala de los datos, se implemento minmax
from sklearn.preprocessing import MinMaxScaler #libreria de machine learning de python
sc = MinMaxScaler(feature_range = (0, 1))      #funcion de escalamiento
training_set_scaled = sc.fit_transform(training_set)

#creating a data structure with N timesteps and 1 output
N = 80   #numero de timesteps 
X_train = []
Y_train = []
for i in range (N,len(training_set)):
    X_train.append(training_set_scaled[i-N:i, 0])
    Y_train.append(training_set_scaled[i, 0])
X_train, Y_train = np.array(X_train), np.array(Y_train)

#remodelar los datos de entrada estructura( muestras, pasos de tiempo, 1) ya que esto lo requiere el LSTM
X_train = np.reshape(X_train, (X_train.shape[0], X_train.shape[1], 1))

#part 2 - construyendo la RNN

#importando librerias y paquetes de keras

from keras.models import Sequential
from keras.layers import Dense
from keras.layers import LSTM
from keras.layers import Dropout

#inicializando la red 
regressor = Sequential()

#añadiendo la primera capa LSTM y una regularizacon droput del 20%
regressor.add(LSTM(units = 50, return_sequences = True, input_shape =(X_train.shape[1], 1)))
regressor.add(Dropout(0.2))

#añadiendo segunda capa LSTM y una regularizacon droput del 20%
regressor.add(LSTM(units = 50, return_sequences = True))
regressor.add(Dropout(0.2))

#añadiendo tercera capa LSTM y una regularizacon droput del 20%
regressor.add(LSTM(units = 50, return_sequences = True))
regressor.add(Dropout(0.2))

#añadiendo una cuarta capa LSTM y una regularizacon droput del 20%
regressor.add(LSTM(units = 50))
regressor.add(Dropout(0.2))

#añadiendo la capa de salida
regressor.add(Dense(units = 1))

#compilando la red
regressor.compile(optimizer = 'adam', loss = 'mean_squared_error')

#ajustando la red a los datos de entrenamiento
regressor.fit(X_train, Y_train, epochs = 100, batch_size = 32)

#consiguiendo los datos del 2021
dataset_test = pd.read_csv('COP=X_2021.csv', index_col='Date', parse_dates=True)
dataset_test.head()

dataset_test.info()

real_price = dataset_test.iloc[:, 3:4].values

test_set = dataset_test['Close']
test_set = pd.DataFrame(test_set)

test_set.info()

#consiguiendo los datos del 2021
dataset_total = pd.concat((dataset['Close'], dataset_test['Close']), axis = 0)
inputs = dataset_total[len(dataset_total)-len(dataset_test)-N:].values
inputs = inputs.reshape(-1,1)
inputs = sc.transform(inputs)
X_test = []
for i in range(N,len(test_set)+N):
    X_test.append(inputs[i-N:i, 0])
X_test = np.array(X_test)
X_test = np.reshape(X_test, (X_test.shape[0], X_test.shape[1], 1))
predicted_price = regressor.predict(X_test)
predicted_price = sc.inverse_transform(predicted_price)

predicted_price = pd.DataFrame(predicted_price)
predicted_price.info()

#visualizacion

plt.figure(figsize=(14,7))

fig, ax = plt.subplots()

plt.plot(real_price, color = 'red', label = 'Precio real (test)')
plt.plot(predicted_price, color = 'blue', label = 'Precio dado por la Red(LSTM)')
plt.title('Precio del Dolar 2021')
plt.xlabel('Tiempo')
plt.ylabel('Precio')
plt.legend()

image_format = 'eps' # e.g .png, .svg, etc.
image_name = 'Red_LSTM.eps'

fig.savefig(image_name, format=image_format, dpi=1200)

plt.show()

import math
from sklearn.metrics import mean_squared_error
rmse = math.sqrt(mean_squared_error(real_price,predicted_price))
print( "the root mean squared error is {}".format(rmse))

df = dataset

df1=df.reset_index()['Close']

#plt.plot(df1)

df1=sc.fit_transform(np.array(df1).reshape(-1,1))

##splitting dataset into train and test split
training_size=int(len(df1)*0.0)
test_size=len(df1)-training_size
train_data,test_data=df1[0:training_size,:],df1[training_size:len(df1),:1]

len(test_data)

x_input=test_data[len(test_data)-N:].reshape(1,-1)
x_input.shape

temp_input=list(x_input)
temp_input=temp_input[0].tolist()

# obteniendo datos de los primeros 30 dias de enero 2021
from numpy import array

lst_output=[]
n_steps=N
i=0
while(i<30):
    
    if(len(temp_input)>N):
        #print(temp_input)
        x_input=np.array(temp_input[1:])
        #print("{} day input {}".format(i,x_input))
        x_input=x_input.reshape(1,-1)
        x_input = x_input.reshape((1, n_steps, 1))
        #print(x_input)
        yhat = regressor.predict(x_input, verbose=0)
        #print("{} day output {}".format(i,yhat))
        temp_input.extend(yhat[0].tolist())
        temp_input=temp_input[1:]
        #print(temp_input)
        lst_output.extend(yhat.tolist())
        i=i+1
    else:
        x_input = x_input.reshape((1, n_steps,1))
        yhat = regressor.predict(x_input, verbose=0)
        #print(yhat[0])
        temp_input.extend(yhat[0].tolist())
        #print(len(temp_input))
        lst_output.extend(yhat.tolist())
        i=i+1
    

#print(lst_output)

day_new=np.arange(1,N+1)
day_pred=np.arange(N+1,N+31)

#len(df1)

#plt.plot(day_new,sc.inverse_transform(df1[len(test_data)-N:]))
#plt.plot(day_pred,sc.inverse_transform(lst_output))

df3=df1.tolist()
df3.extend(lst_output)
#plt.plot(df3[1200:])

df3=sc.inverse_transform(df3).tolist()

data_set2 = pd.read_csv('2016-enero2021.csv', index_col='Date', parse_dates=True)

data_set1=data_set2.dropna()

#data_set1['Close'][1200:].plot(figsize=(16,6))

#plt.figure(figsize=(16,8))
#plt.plot(df3[1200:])

auxiliar=[]
for i in range(0,98):
    auxiliar.append(i)
#print(auxiliar)

import matplotlib.pyplot as plt

#fig, ax = plt.subplots()

plt.plot(auxiliar, data_set1['Close'][1200:], color = 'red', label = 'Precio real')
plt.plot(df3[1200:], color= 'blue', label = 'Precio predicho (30 dias)')
plt.title('Precio del Dolar 2021')
plt.xlabel('Tiempo')
plt.ylabel('Precio')
plt.legend()

#image_format = 'eps' # e.g .png, .svg, etc.
#image_name = '30dias.eps'

#fig.savefig(image_name, format=image_format, dpi=1200)
plt.show()







