from __future__ import absolute_import
import numpy as np
import tensorflow as tf
import sys
from data.song import Song
import json
import tensorflow
from datetime import datetime
import numpy
import csv
import os
from sklearn.preprocessing import normalize
from sklearn.preprocessing import OneHotEncoder
from keras.utils import np_utils
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import Dropout
from keras.layers import LSTM
from keras.layers import Activation
from keras.optimizers import Adam
import json
import glob
import copy
from numpy.random import choice
from music21 import roman, stream, note
from src.utils import get_project_root

ROOT_DIR = get_project_root()

def getAllSongs(midiDir):
	songs = []
	for file in glob.glob(ROOT_DIR + '/midis/' + midiDir + "/*.mid"):
		song = Song(file)
		songs.append(song)
	print(songs)
	return songs


def getMap(songs, modelName):
	durations = []
	for song in songs:
		prog = song.getDurationProgression()
		for item in prog:
			if item not in durations:
				durations.append(item)
	mapping =  dict((item, number) for number, item in enumerate(durations))
	with open(ROOT_DIR + '/files/mappings/'+ modelName + '_durations.json', 'w') as f:
		f.write(json.dumps(mapping))
	return mapping


def prepareDurations(progression, mapping, sequenceLen):
	inputs = []
	outputs = []

	for i in range(0, len(progression) - sequenceLen, 1):
		progIn = progression[i:i + sequenceLen]
		progOut = progression[i + sequenceLen]
		inputs.append([mapping[item] for item in progIn])
		outputs.append(mapping[progOut])
	
	nSequences = len(inputs)

	inputs = np_utils.to_categorical(inputs, num_classes=len(mapping))
	inputs = numpy.reshape(inputs, (nSequences, sequenceLen, len(mapping)))
	outputs = np_utils.to_categorical(outputs, num_classes =len(mapping))
	inputs = inputs / len(mapping)

	return inputs, outputs


def trainDuration(songs, mapping, sequenceLen, epochs):
	progressions = []
	preparedInputs = False
	minLen = 2 * sequenceLen
	for song in songs:
		durations = song.getDurationProgression()
		if len(durations) > minLen:
			progressions.append(durations)
			print(durations)
	

	model = lstm(sequenceLen, len(mapping))
	for progression in progressions:
		inputs, outputs = prepareDurations(progression, mapping, sequenceLen)
		model.fit(inputs, outputs, epochs=epochs, batch_size=128)
		try:
			preparedInputs = numpy.concatenate((preparedInputs, inputs))
		except:
			preparedInputs = inputs
	#	preparedInputs.append(inputs)

	return preparedInputs, model
	

def lstm(sequenceLen, nNotes):
	model = Sequential()
	model.add(LSTM(
			256,
			input_shape=(sequenceLen, nNotes),
			return_sequences=True
		))
	model.add(Dropout(0.3))
	model.add(LSTM(512, return_sequences=True))

	model.add(Dropout(0.3))
	model.add(LSTM(256))
	model.add(Dense(256))
	model.add(Dropout(0.3))
	model.add(Dense(nNotes))
	model.add(Activation('softmax'))
	optimizer = Adam(lr=0.001, beta_1=0.9, beta_2=0.999, epsilon=None, decay=0.0, amsgrad=False)
	#optimizer = "rmsprop"
	model.compile(loss='categorical_crossentropy', optimizer=optimizer)
	return model



def saveModel(model, modelName):
	modelFile = ROOT_DIR + '/files/models/duration/model_' + modelName + '.json'
	weightFile = ROOT_DIR + '/files/models/duration/weights_' + modelName + '.h5'

	# serialize model to JSON
	model_json = model.to_json()
	with open(modelFile, "w") as json_file:
		json_file.write(model_json)
	# serialize weights to HDF5
	model.save_weights(weightFile)

def loadModel(modelName):
	modelFile = ROOT_DIR + '/files/models/duration/model_' + modelName + '.json'
	weightFile = ROOT_DIR + '/files/models/duration/weights_' + modelName + '.h5'

	# load json and create model
	json_file = open(modelFile, 'r')
	loaded_model_json = json_file.read()
	json_file.close()
	loaded_model = model_from_json(loaded_model_json)

	# load weights into new model
	loaded_model.load_weights(weightFile)

	return loaded_model


if __name__ == '__main__':
	sequenceLen = 24
	nNotes = 300
	epochs = 250
	midiDir = 'test_midis'
	modelName = 'allTest_duration'
	songs = getAllSongs(midiDir)
	mapping = getMap(songs, modelName)
	noteInputs, model = trainDuration(songs, mapping, sequenceLen, epochs)
	saveModel(model, modelName)