import sys
from data.song import Song
from datetime import datetime
import numpy as np
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


def prepare_sequences(sequence, sequence_len, n_clusters):
	inputs = []
	outputs = []

	for i in range(0, len(sequence) - sequence_len, 1):
		prog_in = sequence[i:i + sequence_len]
		prog_out = sequence[i + sequence_len]
		inputs.append(prog_in)
		outputs.append(prog_out)
	
	n_sequences = len(inputs)
	print(n_clusters)
	inputs = np_utils.to_categorical(inputs, num_classes=n_clusters)
	inputs = np.reshape(inputs, (n_sequences, sequence_len, n_clusters))
	outputs = np_utils.to_categorical(outputs, num_classes=n_clusters)
	inputs = inputs / n_clusters

	return inputs, outputs



def diversity_check(sequence):
	#use the index of dispersion here as a filter
	iod = np.var(sequence)/np.mean(sequence)
	if iod > 1:
		return True
	else:
		return False


def train_sequences(songs, sequence_len, epochs, n_mes, n_clusters):
	sequences = []
	prepared_inputs = False
	for song in songs:
		sequence = song.get_cluster_sequence(n_mes=n_mes, n_clusters=n_clusters)
		if isinstance(sequence, (np.ndarray, np.generic,)):
			if diversity_check(sequence):
				sequences.append(sequence)


	model = lstm(sequence_len, n_clusters)
	for sequence in sequences:
		inputs, outputs = prepare_sequences(sequence, sequence_len, n_clusters)
		es = EarlyStopping(monitor='loss', mode='min', verbose=1,  min_delta=0, patience=100)

		model.fit(inputs, outputs, epochs=epochs, batch_size=128, callbacks=[es])
		try:
			prepared_inputs = np.concatenate((prepared_inputs, inputs))
		except:
			prepared_inputs = inputs


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
	model_file = ROOT_DIR + '/files/models/sequence/model_' + model_name + '.json'
	weight_file = ROOT_DIR + '/files/models/sequence/weights_' + model_name + '.h5'

	# serialize model to JSON
	model_json = model.to_json()
	with open(model_file, "w") as json_file:
		json_file.write(model_json)
	# serialize weights to HDF5
	model.save_weights(weight_file)


if __name__ == '__main__':
	sequence_len = 4
	epochs = 500
	midi_dir = 'test_midis'
	model_name = 'sequence_build'
	n_mes = 2
	n_clusters = 20
	songs = get_all_songs(midi_dir)
	note_inputs, model = train_sequences(songs, sequence_len, epochs, n_mes, n_clusters)
	save_model(model, model_name)