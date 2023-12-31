# -*- coding: utf-8 -*-
"""TS_Dicoding.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/11mTRZ3Fh5m418KK3xx4pHVjtW_OCQ2hx

# Perkenalan

Perkenalkan nama saya Wildan Abdurrasyid seorang Mahasiswa sem 3 Institut Teknologi Tangerang Selatan.

pada proyek ini saya akan membuat Model TS (Time Series) sederhana dari dataset yang telah saya dapatkan.

link source dataset: https://www.kaggle.com/datasets/hmavrodiev/london-bike-sharing-dataset/
"""

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from keras.layers import Dense, LSTM, Dropout, Bidirectional
import matplotlib.pyplot as plt
import tensorflow as tf

df = pd.read_csv('london_merged.csv')
df = df[['timestamp', 'cnt']]
df

df['timestamp'] = pd.to_datetime(df['timestamp'].astype(str))
df.info()

scaler = MinMaxScaler()
df['cnt'] = scaler.fit_transform(df['cnt'].values.reshape(-1, 1)).flatten()
X = df['timestamp'].values
Y  = df['cnt'].values
plt.figure(figsize=(15,5))
plt.plot(X, Y)
plt.title('Time plot', fontsize=20);

# Split data into training and validation sets
train_size = int(len(df) * 0.8)
train_data, test_data = df[:train_size], df[train_size:]
train_data, test_data

"""## Define windowed dataset function"""

def windowed_dataset(series, window_size, batch_size, shuffle_buffer):
    series = tf.expand_dims(series, axis=-1)
    ds = tf.data.Dataset.from_tensor_slices(series)
    ds = ds.window(window_size + 1, shift=1, drop_remainder=True)
    ds = ds.flat_map(lambda w: w.batch(window_size + 1))
    ds = ds.shuffle(shuffle_buffer)
    ds = ds.map(lambda w: (w[:-1], w[-1:]))
    ds = ds.batch(batch_size).prefetch(1)
    return ds.repeat()

train_set = windowed_dataset(train_data['cnt'].values, window_size=60, batch_size=100, shuffle_buffer=1000)
val_set = windowed_dataset(test_data['cnt'].values, window_size=60, batch_size=100, shuffle_buffer=1000)

steps_per_epoch_train = len(train_data) // 100
steps_per_epoch_val = len(test_data) // 100

"""## Build the model"""

model = tf.keras.models.Sequential([
    tf.keras.layers.Bidirectional(tf.keras.layers.LSTM(128, return_sequences=True, input_shape=[None, 1])),
    tf.keras.layers.Bidirectional(tf.keras.layers.LSTM(128)),
    tf.keras.layers.Dropout(rate=0.5),
    tf.keras.layers.Dense(120, activation="relu"),
    tf.keras.layers.Dense(30, activation="relu"),
    tf.keras.layers.Dense(30, activation="relu"),
    tf.keras.layers.Dense(1)
])

"""## Fungsi Callbacks"""

threshold_mae = (df['cnt'].max() - df['cnt'].min()) * 10/100
class my_callback(tf.keras.callbacks.Callback):
    def on_epoch_end(self, epoch, logs={}):
        if(logs.get('mae') < threshold_mae and logs.get('val_mae') < threshold_mae):
            print(" \n MAE dari model < 10% skala data")
            self.model.stop_training = True

callbacks = my_callback()

"""## Compile the model"""

optimizer = tf.keras.optimizers.SGD(learning_rate=1.0000e-01, momentum=0.9)
model.compile(loss=tf.keras.losses.Huber(),
              optimizer = optimizer,
              metrics=["mae"])

"""## Train the model with validation data"""

history = model.fit(train_set, epochs=50, steps_per_epoch=steps_per_epoch_train,
                    validation_data=val_set, validation_steps=steps_per_epoch_val,
                    callbacks=[callbacks])

import matplotlib.pyplot as plt
plt.plot(history.history['mae'], label='Training Mae')
plt.plot(history.history['val_mae'], label='Validation Mae')
plt.xlabel('Epochs')
plt.ylabel('Mae')
plt.legend()
plt.show()

plt.plot(history.history['loss'], label='Training Loss')
plt.plot(history.history['val_loss'], label='Validation Loss')
plt.xlabel('Epochs')
plt.ylabel('Loss')
plt.legend()
plt.show()