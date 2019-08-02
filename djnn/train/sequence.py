import sys
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
from djnn import ROOT_DIR
from djnn.data import song


class SequenceModel():

	def __init__(self, song_objs, n_clusters, n_measures, sequence_len, midi_dir, model_name, instrument=None):

		self.model_name = model_name
		self.songs = song_objs
		self.n_clusters = n_clusters
		self.n_measures = n_measures
		self.sequences = []
		self.inputs = []
		self.outputs = []
		self.mapping = None
		self.sequence_len = sequence_len
		self.prepare_sequences()

	def get_all_sequences(self):

		for song in self.songs:
			sequence = obj.get_cluster_sequence(n_mes=self.n_measures, n_clusters=self.n_clusters)
			
			if np.var(sequence)/np.mean(sequence) > 1:
				self.sequences.append(sequence)


	def prepare_sequences(self):

		for sequence in self.sequences:

			for i in range(0, len(sequence) - self.sequence_len, 1):
				prog_in = sequence[i:i + self.sequence_len]
				prog_out = sequence[i + self.sequence_len]
				inputs.append(prog_in)
				outputs.append(prog_out)
			
			n_sequences = len(inputs)
			inputs = np_utils.to_categorical(inputs, num_classes=self.n_clusters)
			inputs = np.reshape(inputs, (n_sequences, self.sequence_len, self.n_clusters))
			outputs = np_utils.to_categorical(outputs, num_classes=self.n_clusters)
			inputs = inputs / self.n_clusters

			self.inputs.append(inputs)
			self.outputs.append(outputs)

	def train_sequences(self, epochs):

		model = self.lstm()
		for sequence in self.sequences:
			es = EarlyStopping(monitor='loss', mode='min', verbose=1,  min_delta=0, patience=100)
			model.fit(self.inputs, self.outputs, epochs=epochs, batch_size=128, callbacks=[es])

		self.save_model(model)


	def lstm(self):
		model = Sequential()
		model.add(LSTM(
				256,
				input_shape=(self.sequence_len, self.n_clusters),
				return_sequences=True
			))
		model.add(Dropout(0.3))
		model.add(LSTM(512, return_sequences=True))

		model.add(Dropout(0.3))
		model.add(LSTM(256))
		model.add(Dense(256))
		model.add(Dropout(0.3))
		model.add(Dense(self.n_clusters))
		model.add(Activation('softmax'))
		optimizer = Adam(lr=0.001, beta_1=0.9, beta_2=0.999, epsilon=None, decay=0.0, amsgrad=False)
		#optimizer = "rmsprop"
		model.compile(loss='categorical_crossentropy', optimizer=optimizer )
		return model


	def save_model(self, model):
		model_file = ROOT_DIR + '/files/models/sequence/model_' + self.model_name + '.json'
		weight_file = ROOT_DIR + '/files/models/sequence/weights_' + self.model_name + '.h5'

		# serialize model to JSON
		model_json = model.to_json()
		with open(model_file, "w") as json_file:
			json_file.write(model_json)
		# serialize weights to HDF5
		model.save_weights(weight_file)



if __name__ == '__main__':
	sequence_len = 12
	epochs = 50
	midi_dir = 'small_test'
	model_name = 'class_test'
	n_measures = 50
	n_clusters = 15
	sequence_len = 20

	song_objs = song.get_all_songs(midi_dir)
	harmony_model = SequenceModel(song_objs, n_clusters, n_measures, sequence_len, midi_dir, model_name)
	harmony_model.train_sequences(5)
