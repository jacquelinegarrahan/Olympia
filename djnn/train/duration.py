from __future__ import absolute_import
import sys
from data.song import Song
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
from keras.callbacks import EarlyStopping
import json
import glob
import copy
from numpy.random import choice
from music21 import roman, stream, note
from src.utils import get_project_root

ROOT_DIR = get_project_root()

def get_all_songs(midi_dir):
	songs = []
	for file in glob.glob(ROOT_DIR + '/midis/' + midi_dir + "/*.mid"):
		song = Song(file)
		songs.append(song)
	return songs


def get_map(songs, model_name):
	durations = []
	for song in songs:
		prog = song.get_duration_progression()
		for item in prog:
			if item not in durations:
				durations.append(item)
	mapping =  dict((item, number) for number, item in enumerate(durations))
	with open(ROOT_DIR + '/files/mappings/'+ model_name + '_durations.json', 'w') as f:
		f.write(json.dumps(mapping))
	return mapping


def prepare_durations(progression, mapping, sequence_len):
	inputs = []
	outputs = []

	for i in range(0, len(progression) - sequence_len, 1):
		prog_in = progression[i:i + sequence_len]
		prog_out = progression[i + sequence_len]
		inputs.append([mapping[item] for item in prog_in])
		outputs.append(mapping[prog_out])
	
	n_sequences = len(inputs)

	inputs = np_utils.to_categorical(inputs, num_classes=len(mapping))
	inputs = numpy.reshape(inputs, (n_sequences, sequence_len, len(mapping)))
	outputs = np_utils.to_categorical(outputs, num_classes =len(mapping))
	inputs = inputs / len(mapping)

	return inputs, outputs



def diversity_check(duration):
	#use the index of dispersion here as a filter
	iod = numpy.var(duration)/numpy.mean(duration)
	if iod > 1:
		return True
	else:
		return False


def train_duration(songs, mapping, sequence_len, epochs):
	progressions = []
	prepared_inputs = False
	minLen = 2 * sequence_len
	for song in songs:
		durations = song.get_duration_progression()
		if len(durations) > minLen:
			if diversity_check(durations):
				progressions.append(durations)
	

	model = lstm(sequence_len, len(mapping))
	for progression in progressions:
		inputs, outputs = prepare_durations(progression, mapping, sequence_len)
		n_train = int(0.9*len(inputs))
		es = EarlyStopping(monitor='loss', mode='min', verbose=1,  min_delta=0, patience=25)

		model.fit(inputs, outputs, epochs=epochs, batch_size=128, callbacks=[es])
		try:
			prepared_inputs = numpy.concatenate((prepared_inputs, inputs))
		except:
			prepared_inputs = inputs
		print('Not terminating early...')


	return prepared_inputs, model
	

def lstm(sequence_len, n_notes):
	model = Sequential()
	model.add(LSTM(
			256,
			input_shape=(sequence_len, n_notes),
			return_sequences=True
		))
	model.add(Dropout(0.3))
	model.add(LSTM(512, return_sequences=True))

	model.add(Dropout(0.3))
	model.add(LSTM(256))
	model.add(Dense(256))
	model.add(Dropout(0.3))
	model.add(Dense(n_notes))
	model.add(Activation('softmax'))
	optimizer = Adam(lr=0.001, beta_1=0.9, beta_2=0.999, epsilon=None, decay=0.0, amsgrad=False)
	#optimizer = "rmsprop"
	model.compile(loss='categorical_crossentropy', optimizer=optimizer )
	return model



def save_model(model, model_name):
	model_file = ROOT_DIR + '/files/models/duration/model_' + model_name + '.json'
	weight_file = ROOT_DIR + '/files/models/duration/weights_' + model_name + '.h5'

	# serialize model to JSON
	model_json = model.to_json()
	with open(model_file, "w") as json_file:
		json_file.write(model_json)
	# serialize weights to HDF5
	model.save_weights(weight_file)

def load_model(model_name):
	model_file = ROOT_DIR + '/files/models/duration/model_' + model_name + '.json'
	weight_file = ROOT_DIR + '/files/models/duration/weights_' + model_name + '.h5'

	# load json and create model
	json_file = open(modelFile, 'r')
	loaded_model_json = json_file.read()
	json_file.close()
	loaded_model = model_from_json(loaded_model_json)

	# load weights into new model
	loaded_model.load_weights(weight_file)

	return loaded_model


if __name__ == '__main__':
	sequence_len = 24
	epochs = 50
	midi_dir = 'test_midis'
	model_name = 'allTest_duration'
	songs = get_all_songs(midi_dir)
	mapping = get_map(songs, model_name)
	note_inputs, model = train_duration(songs, mapping, sequence_len, epochs)
	save_model(model, model_name)