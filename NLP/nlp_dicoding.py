# -*- coding: utf-8 -*-
"""NLP_Dicoding.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1dIAcP5kMASghxPy1aW3XByK_24y0t70J

# Perkenalan

Perkenalkan nama saya Wildan Abdurrasyid seorang Mahasiswa sem 3 Institut Teknologi Tangerang Selatan.

pada proyek ini saya akan membuat Model NLP (Natural Language processing) sederhana dari dataset yang telah saya dapatkan.

link source dataset: https://www.kaggle.com/datasets/andrewmvd/cyberbullying-classification
"""

import pandas as pd
df = pd.read_csv('cyberbullying_tweets.csv')
df

"""## Text Cleaning"""

import re
import nltk
import string
from wordcloud import WordCloud
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.stem.snowball import SnowballStemmer
from sklearn.feature_extraction.text import CountVectorizer
nltk.download('omw-1.4')
nltk.download('stopwords')
nltk.download('punkt')
Stopwords = set(stopwords.words('english'))
def clean(text):
    text = text.lower() #Converting to lowerCase
    text = re.sub('[%s]' % re.escape(string.punctuation), ' ',text) #removing punctuation

    text_tokens = word_tokenize(text) #removing stopwords
    tw = [word for word in text_tokens if not word in Stopwords]
    text = (" ").join(tw)

    splt = text.split(' ')
    output = [x for x in splt if len(x) > 3] #removing words with length<=3
    text = (" ").join(output)

    text = re.sub(r"\s+[a-zA-Z]\s+", ' ', text) #removing single character
    text = re.sub('<.*?>+',' ',text) #removing HTML Tags
    text = re.sub('\n', ' ',text) #removal of new line characters
    text = re.sub(r'\s+', ' ',text) #removal of multiple spaces
    return text

df['tweet_text'] = df['tweet_text'].apply(clean)

"""## Preproses Data"""

nltk.download('wordnet')
def data_preprocessing(text):
    tokens = word_tokenize(text) #Tokenization
    tokens = [WordNetLemmatizer().lemmatize(word) for word in tokens] #Lemmetization
    tokens = [SnowballStemmer(language = 'english').stem(word) for word in tokens] #Stemming
    return " ".join(tokens)

df['tweet_text'] = df['tweet_text'].apply(data_preprocessing)

"""## one-hot-encoding dan membuat dataframe baru."""

category = pd.get_dummies(df.cyberbullying_type)
df_baru = pd.concat([df, category], axis=1)
df_baru = df_baru.drop(columns='cyberbullying_type')
df_baru

text_column = 'tweet_text'
genre_columns = ['age', 'ethnicity', 'gender', 'not_cyberbullying', 'other_cyberbullying', 'religion']
X = df_baru[text_column].values
Y = df_baru[genre_columns].values

"""## Pembagian Data Training dan Testing"""

from sklearn.model_selection import train_test_split
x_train, x_test, y_train, y_test = train_test_split(X, Y, test_size=0.2)

"""##  Tokenisasi"""

from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
tokenizer = Tokenizer(num_words=5000, oov_token='x')
tokenizer.fit_on_texts(x_train)

sequences_train = tokenizer.texts_to_sequences(x_train)
sequences_test = tokenizer.texts_to_sequences(x_test)

padded_train = pad_sequences(sequences_train, padding='post', maxlen=100, truncating='post')
padded_test = pad_sequences(sequences_test, padding='post', maxlen=100, truncating='post')

"""## Modelling dan Compile"""

import tensorflow as tf
from tensorflow.keras.layers import Bidirectional, LSTM

model = tf.keras.Sequential([
    tf.keras.layers.Embedding(input_dim=5000, output_dim=16),  # Increased output_dim
    Bidirectional(LSTM(128, return_sequences=True)),  # Bidirectional LSTM
    Bidirectional(LSTM(64)),
    tf.keras.layers.Dense(128, activation='relu'),  # Increased number of units
    tf.keras.layers.Dropout(0.5),
    tf.keras.layers.Dense(64, activation='relu'),
    tf.keras.layers.Dense(len(genre_columns), activation='softmax')
])

model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])

"""## Fungsi Callbacks"""

class myCallback(tf.keras.callbacks.Callback):
    def on_epoch_end(self, epoch, logs={}):
        if logs.get('accuracy') > 0.9 and logs.get('val_accuracy') > 0.9:
            print("\nAkurasi telah mencapai >90%!")
            self.model.stop_training = True

callbacks = myCallback()

"""## Latih Data dengan Callbacks"""

num_epochs = 10
history = model.fit(padded_train, y_train, epochs=num_epochs, validation_data=(padded_test, y_test), callbacks=[callbacks], verbose=2)

"""## Evaluate accuracy"""

train_accuracy = model.evaluate(padded_train, y_train, verbose=0)[1]
test_accuracy = model.evaluate(padded_test, y_test, verbose=0)[1]

print(f'Training Accuracy: {train_accuracy * 100:.2f}%')
print(f'Test Accuracy: {test_accuracy * 100:.2f}%')

"""## Plot loss and accuracy"""

import matplotlib.pyplot as plt
plt.plot(history.history['accuracy'], label='Training Accuracy')
plt.plot(history.history['val_accuracy'], label='Validation Accuracy')
plt.xlabel('Epochs')
plt.ylabel('Accuracy')
plt.legend()
plt.show()

plt.plot(history.history['loss'], label='Training Loss')
plt.plot(history.history['val_loss'], label='Validation Loss')
plt.xlabel('Epochs')
plt.ylabel('Loss')
plt.legend()
plt.show()