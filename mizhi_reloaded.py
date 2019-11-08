# -*- coding: utf-8 -*-
"""Mizhi_Reloaded.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/172NrI0Jro3_lO2wLkZBMpn_7T4Rk8FAE
"""

# Commented out IPython magic to ensure Python compatibility.
# Load the Drive helper and mount
from google.colab import drive

# This will prompt for authorization.
drive.mount('/content/drive')
# %cd ./drive/My\ Drive

!mkdir -p drive
!google-drive-ocamlfuse drive

!pip install -q keras

import warnings
warnings.filterwarnings('ignore')

import os 
import numpy as np 
import imutils
from imutils import paths
import random
import cv2
from keras.preprocessing.image import img_to_array
from keras.optimizers import Adam
from sklearn.model_selection import train_test_split
from keras.utils import to_categorical
import matplotlib.pyplot as plt

# initialize the data and labels
print("[INFO] loading images...")
data = []
labels = []

imagePaths = sorted(list(paths.list_images('MIZHI')))
random.seed(42)
random.shuffle(imagePaths)

# loop over the input images
for imagePath in imagePaths:
    image = cv2.imread(imagePath)
    image = cv2.resize(image, (28, 28))
    image = img_to_array(image)
    data.append(image)
    # extract the class label from the image path and update the
    # labels list
    label = imagePath.split(os.path.sep)[-2]
    label = 1 if label == "MVD" else 0
    labels.append(label)

print(imagePaths)

print(labels)

data = np.array(data, dtype="float") / 255.0
labels = np.array(labels)

# partition the data into training and testing splits using 75% of the data for training and the remaining 25% for testing
(trainX, testX, trainY, testY) = train_test_split(data, labels, test_size=0.25, random_state=42)

trainY = to_categorical(trainY)
testY = to_categorical(testY)

from keras import layers
from keras import models
from keras.layers import Dense, Dropout, Flatten, Conv2D, MaxPooling2D

model = models.Sequential()
model.add(layers.Conv2D(32, (3, 3), activation='relu', input_shape=(28, 28, 3)))
model.add(layers.MaxPooling2D((2, 2)))
model.add(Dropout(0.25))
model.add(layers.Conv2D(64, (3, 3), activation='relu'))
model.add(layers.MaxPooling2D((2, 2)))
model.add(Dropout(0.25))
model.add(layers.Conv2D(64, (3, 3), activation='relu'))
model.add(layers.MaxPooling2D((2, 2)))
model.add(Dropout(0.25))
model.summary()

model.add(layers.Flatten())
model.add(layers.Dense(512, activation='relu'))
model.add(layers.Dense(512, activation='relu'))
model.add(Dropout(0.25))
model.add(layers.Dense(2, activation='softmax'))
model.summary()

model.compile(optimizer='rmsprop', loss='categorical_crossentropy', metrics=['accuracy'])
model.fit(trainX, trainY, epochs=50, batch_size=55)

test_loss, test_acc = model.evaluate(testX, testY)

test_acc

#print(cv2.__version__)
#load the image
image = cv2.imread('MIZHI/test/er.jpg')
orig = image.copy()

image = cv2.resize(image, (28, 28))
image = image.astype("float") / 255.0
image = img_to_array(image)
image = np.expand_dims(image, axis=0)

(WA, MVD) = model.predict(image)[0]

label = "MVD" if MVD > WA else "WA"
proba = MVD if MVD > WA else WA
label = "{}: {:.2f}%".format(label, proba * 100)

# draw the label on the image
output = imutils.resize(orig, width=400)
cv2.putText(output, label, (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

# show the output image
from google.colab.patches import cv2_imshow
cv2_imshow(output)
cv2.waitKey(0)

from keras.models import model_from_json
# serialize model to JSON
model_json = model.to_json()

# Write the file name of the model

with open("mizhi.json", "w") as json_file:
    json_file.write(model_json)
    
# serialize weights to HDF5
# Write the file name of the weights

model.save_weights("mizhi.h5")
print("Saved model to disk")

