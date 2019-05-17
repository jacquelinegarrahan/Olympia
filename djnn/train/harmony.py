import numpy
import sys
from data.song import Song
import json
import tensorflow
from datetime import datetime
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
	notes = []
	for song in songs:
		rns = song.convert_harmonic_to_roman_numerals()
		for item in rns:
			if item not in notes:
				notes.append(item)
	mapping =  dict((item, number) for number, item in enumerate(notes))
	with open(ROOT_DIR + '/files/mappings/'+ model_name + '_harmony.json', 'w') as f:
		f.write(json.dumps(mapping))
	return mapping



def prepare_harmonies(progression, mapping, sequence_len):
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


def diversity_check(harmonics, mapping):
	#use the index of dispersion here as a filter
	harm_vec = [mapping[harm] for harm in harmonics]
	iod = numpy.var(harm_vec)/numpy.mean(harm_vec)
	if iod > 10:
		return True
	else:
		return False


def train_harmonies(songs, mapping, sequence_len, epochs):
	progressions = []
	prepared_inputs = False
	minLen = 2 * sequence_len
	for song in songs:
		rns = song.convert_harmonic_to_roman_numerals()
		if len(rns) > minLen:
			if diversity_check(rns, mapping):
				progressions.append(rns)

	model = lstm(sequence_len, len(mapping))
	for progression in progressions:
		inputs, outputs = prepare_harmonies(progression, mapping, sequence_len)
		n_train = int(0.9*len(inputs))
		es = EarlyStopping(monitor='loss', mode='min', verbose=1,  min_delta=0, patience=100)
		model.fit(inputs, outputs, epochs=epochs, batch_size=128, callbacks=[es])
		try:
			prepared_inputs = numpy.concatenate((prepared_inputs, inputs))
		except:
			prepared_inputs = inputs
	#	preparedInputs.append(inputs)

	return prepared_inputs, model
	

def lstm(sequence_len, n_notes):
	model = Sequential()
	model.add(LSTM(
			256,
			input_shape=(sequence_len, n_notes),
			return_sequences=True
		))
	model.add(Dropout(0.1))
	model.add(LSTM(512, return_sequences=True))
	model.add(Dropout(0.1))
	model.add(LSTM(256))
	model.add(Dense(256))
	model.add(Dropout(0.1))
	model.add(Dense(n_notes))
	model.add(Activation('softmax'))
	optimizer = Adam(lr=0.001, beta_1=0.9, beta_2=0.999, epsilon=None, decay=0.0, amsgrad=False)
	#optimizer = "rmsprop"
	model.compile(loss='categorical_crossentropy', optimizer=optimizer)
	return model


def convert_notes(inputs, note_map):
	notes = []
	for input in inputs:
		idx = numpy.argmax(input)
		result = list(note_map.keys())[list(note_map.values()).index(idx)]
		notes.append(result)
	return notes


def save_model(model, model_name):
	model_file = ROOT_DIR + '/files/models/harmony/model_' + model_name + '.json'
	weight_file = ROOT_DIR + '/files/models/harmony/weights_' + model_name + '.h5'

	# serialize model to JSON
	model_json = model.to_json()
	with open(model_file, "w") as json_file:
		json_file.write(model_json)
	# serialize weights to HDF5
	model.save_weights(weight_file)


if __name__ == '__main__':
	sequence_len = 24
	epochs = 500
	midi_dir = 'test_midis'
	model_name = 'harmony_2'
	songs = get_all_songs(midi_dir)
	mapping = get_map(songs, model_name)
	noteInputs, model = train_harmonies(songs, mapping, sequence_len, epochs)
	save_model(model, model_name)