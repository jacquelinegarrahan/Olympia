import sys
from datetime import datetime
import numpy
import csv
import os
from pydantic import BaseModel
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


class DurationSettings(BaseModel):
	




class DurationModel():

	def __init__(self, song_objs, sequence_len, midi_dir, model_name, instrument=None):

		self.model_name = model_name
		self.songs = song_objs
		self.durations = []
		self.inputs = []
		self.outputs = []
		self.mapping = None
		self.sequence_len = sequence_len
		
		self.get_all_durations(instrument=instrument)
		self.build_duration_map()
		self.prepare_input()

	def get_all_durations(self, instrument=None):
		#filter durations by instrument 

		if not instrument:
			for song_obj in self.songs:
				for part in song_obj.parts:
					self.durations.append(part.duration_progression)

		else:
			for song_obj in self.songs:
				print("getting duration for %s " % song_obj.raw_path)
				part = song_obj.get_part_by_instrument(instrument)
				if part:
					self.durations.append(part.duration_progression)

	def build_duration_map(self):
		unique_durations = []
		
		for progression in self.durations:
			for item in progression:
				if item not in unique_durations:
					unique_durations.append(item)

		mapping =  dict((item, dur) for dur, item in enumerate(unique_durations))
		with open(ROOT_DIR + '/djnn/files/mappings/'+ model_name + '_duration.json', 'w') as f:
			f.write(json.dumps(mapping))

		self.mapping = mapping


	def prepare_input(self):
		minLen = 2 * self.sequence_len

		for progression in self.durations:

			if len(progression) >= minLen:

				prog_input = []
				prog_output = []

				for i in range(0, len(progression) - self.sequence_len, 1):
					prog_in = progression[i:i + self.sequence_len]
					prog_out = progression[i + self.sequence_len]
					if set(prog_in) > 3: # we don't want series with only type of note
						prog_input.append([self.mapping[item] for item in prog_in])
						prog_output.append(self.mapping[prog_out])
				
				if prog_input and prog_output:
					n_sequences = len(prog_input)

					categorical_input = np_utils.to_categorical(prog_input, num_classes=len(self.mapping))
					categorical_input = numpy.reshape(categorical_input, (n_sequences, self.sequence_len, len(self.mapping)))
					categorical_output = np_utils.to_categorical(prog_output, num_classes =len(self.mapping))
					categorical_input = categorical_input / len(self.mapping)

					self.inputs.append(categorical_input)
					self.outputs.append(categorical_output)

	def train_duration(self, epochs):
		allowed_progressions = []
		prepared_inputs = False

		model = self.lstm(len(self.mapping))

		es = EarlyStopping(monitor='loss', mode='min', verbose=1,  min_delta=0, patience=100)
		model.fit(self.inputs, self.outputs, epochs=epochs, batch_size=128, callbacks=[es])

		self.save_model(model)

	def lstm(self, n_notes):
		model = Sequential()
		model.add(LSTM(
				256,
				input_shape=(self.sequence_len, n_notes),
				return_sequences=True
			))
		model.add(Dropout(0.3))
		model.add(LSTM(512, return_sequences=True))

		model.add(Dropout(0.2))
		model.add(LSTM(256))
		model.add(Dense(256))
		model.add(Dropout(0.2))
		model.add(Dense(n_notes))
		model.add(Activation('softmax'))
		optimizer = Adam(lr=0.001, beta_1=0.9, beta_2=0.999, epsilon=None, decay=0.0, amsgrad=False)
		#optimizer = "rmsprop"
		model.compile(loss='categorical_crossentropy', optimizer=optimizer)
		return model

	
	def save_model(self, model):
		model_file = ROOT_DIR + '/djnn/files/models/duration/model_' + self.model_name + '.json'
		weight_file = ROOT_DIR + '/djnn/files/models/duration/weights_' + self.model_name + '.h5'

		# serialize model to JSON
		model_json = model.to_json()
		with open(model_file, "w") as json_file:
			json_file.write(model_json)
		# serialize weights to HDF5
		model.save_weights(weight_file)



if __name__ == '__main__':
	sequence_len = 12
	epochs = 50
	midi_dir = 'random_subset'
	model_name = 'duration_test_piano'

	song_objs = song.get_all_songs(midi_dir)
	dur_model = DurationModel(song_objs, sequence_len, midi_dir, model_name, instrument="piano")
	dur_model.train_duration(epochs)

