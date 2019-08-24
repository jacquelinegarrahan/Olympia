from djnn.data.song import Song
from music21 import roman, stream, note, chord, instrument
from keras.models import model_from_json
import json
import numpy as np
from keras.utils import np_utils
import copy
from djnn import ROOT_DIR


class SongBuilder():

	def __init__(self, sequence_model_name, instrument_map, key, n_sections, n_mes):

		self.instrument_map = instrument_map
		self.sequence_model_name = sequence_model_name
		self.n_sections = n_sections
		self.midi_stream = stream.Stream()
		self.key = key
		self.n_notes = n_sections * n_mes * 5 # produce extra for more material
		self.sequence = self.build_sequence()


	def build_sequence(self):
		sequence_model = load_model(self.sequence_model_name, 'sequence')

		n_section_options = sequence_model.output_shape[1]
		sequence_len = sequence_model.input_shape[1]
		start = np.random.choice(range(0, n_section_options), sequence_len)
		sequence = np_utils.to_categorical(start, num_classes=n_section_options)
		sequence = np.reshape(sequence, (1, sequence_len, n_section_options))

		generated_sequence = []

		for i in range(self.n_sections):
			seq_input = copy.deepcopy(sequence)
			seq_val = sequence_model.predict(seq_input, verbose=0)
			seq = np.argmax(seq_val)

			generated_sequence.append(seq)

			next_seq =  np_utils.to_categorical([seq], num_classes=n_section_options)
			next_seq = np.reshape(next_seq, (1, 1, n_section_options))
			next_seq = next_seq/n_section_options
			sequence = np.concatenate((sequence, next_seq), axis = 1)
			sequence = np.delete(sequence, 0, axis=1)

		return generated_sequence


	def build_instrument_part(self, instrument_opt):

		instrument_part = stream.Part()
		if "piano" in instrument_opt:
			instrument_part.append(instrument.Piano())

			start_pitches = {
				"C": [60, 67]
			}

		elif "bass" in instrument_opt:
			instrument_part.append(instrument.Bass())

			start_pitches = {
				"C": [43]
			}

		durations = self.generate_durations(instrument_opt)
		harmony = self.generate_harmony(instrument_opt)

		starting_note = np.random.choice(start_pitches[self.key])
		for i, note_ps_diff in enumerate(harmony):
			new_note = note.Note()
			new_note.durationType = durations[i]
			new_note.offset = instrument_part.highestTime
			new_note.pitch.ps = starting_note + float(harmony[i])
			instrument_part.append(new_note)

		self.midi_stream.append(instrument_part)

	def generate_harmony(self, instrument_opt): 
		harmony_model = load_model(self.instrument_map[instrument_opt]["harmony"], 'harmony')
		n_options = harmony_model.output_shape[1]
		sequence_len = harmony_model.input_shape[1]
		harmony_map = load_mapping(self.instrument_map[instrument_opt]["harmony"], "harmony")
		harmony_sequence = np.random.choice(len(harmony_map), sequence_len)
		harmony_sequence = np_utils.to_categorical(harmony_sequence, num_classes=len(harmony_map))
		harmony_sequence = np.reshape(harmony_sequence, (1, sequence_len, len(harmony_map)))
		generated_harmony = map_values(harmony_sequence, harmony_map)

		for i, note in enumerate(range(self.n_notes)):
			print('generating note %s', i)
			harmonic_input = copy.deepcopy(harmony_sequence)
			harmony_val = harmony_model.predict(harmonic_input, verbose=0)
			harmony_idx = np.argmax(harmony_val)

			harmony = list(harmony_map.keys())[list(harmony_map.values()).index(harmony_idx)]
			generated_harmony.append(harmony)

			#process harmony
			next_harmony =  np_utils.to_categorical([harmony_idx], num_classes=len(harmony_map))
			next_harmony = np.reshape(next_harmony, (1, 1, len(harmony_map)))
			next_harmony = next_harmony/len(harmony_map)
			harmony_sequence = np.concatenate((harmony_sequence, next_harmony), axis = 1)
			harmony_sequence = np.delete(harmony_sequence, 0, axis=1)

		return generated_harmony

	def generate_durations(self, instrument_opt):
		#process duration
		duration_model = load_model(self.instrument_map[instrument_opt]["duration"], 'duration')
		sequence_len = duration_model.input_shape[1]
		duration_map = load_mapping(self.instrument_map[instrument_opt]["duration"], "duration")
		duration_sequence = np.random.choice(len(duration_map), sequence_len)
		duration_sequence = np_utils.to_categorical(duration_sequence, num_classes=len(duration_map))
		duration_sequence = np.reshape(duration_sequence, (1, sequence_len, len(duration_map)))
		generated_duration = map_values(duration_sequence, duration_map)

		for i, note in enumerate(range(self.n_notes)):
			print('generating note %s', i)

			duration_input = copy.deepcopy(duration_sequence)
			duration_val = duration_model.predict(duration_input, verbose=0)
			duration_idx = np.argmax(duration_val)
			duration =  list(duration_map.keys())[list(duration_map.values()).index(duration_idx)]

			#duration = check_duration(duration_val, duration_map, generated_duration)
			generated_duration.append(duration)
			next_duration =  np_utils.to_categorical([duration_map[duration]], num_classes=len(duration_map))
			next_duration = np.reshape(next_duration, (1, 1, len(duration_map)))
			next_duration = next_duration/len(duration_map)
			duration_sequence = np.concatenate((duration_sequence, next_duration), axis = 1)
			duration_sequence = np.delete(duration_sequence, 0, axis=1)

		return generated_duration

	def write_midi(self, song_name):

		save_file = ROOT_DIR + '/djnn/files/songs/' + song_name
		self.midi_stream.write('midi', fp=save_file)







def load_model(model_name, model_type):
	model_file = ROOT_DIR + '/djnn/files/models/' + model_type + '/model_' + model_name + '.json'
	weight_file = ROOT_DIR + '/djnn/files/models/' + model_type + '/weights_' + model_name + '.h5'

	# load json and create model
	json_file = open(model_file, 'r')
	loaded_model_json = json_file.read()
	json_file.close()
	loaded_model = model_from_json(loaded_model_json)

	# load weights into new model
	loaded_model.load_weights(weight_file)
	print('{} loaded!'.format(model_name))

	return loaded_model


def map_values(inputs, note_map):
	notes = []
	for input in inputs:
		idx = np.argmax(input)
		result = list(note_map.keys())[list(note_map.values()).index(idx)]
		notes.append(result)
	return notes


def load_mapping(model_name, model_type):
	mapping =  json.loads(open(ROOT_DIR + '/djnn/files/mappings/' + model_name + '_' + model_type + '.json').read())
	return mapping



def check_duration(duration_val, duration_map, generated_durations):

#	measureOffsetMap() 

	#idx = 
	idx = np.argmax(duration_val)
	float_durations = [float(i) for i in generated_durations]
	duration =  list(duration_map.keys())[list(duration_map.values()).index(idx)]
	benchmark = sum(float_durations) % 4 
	new_benchmark = (sum(float_durations) + float(duration)) % 4

	if benchmark > 0:
		if new_benchmark < benchmark and float(duration) < 4.0 and float(duration) > 0.25:
			return duration
		else:
			return str(benchmark)
	elif benchmark == 0:
		if float(duration) < 4.0 and float(duration) > 0.25:
			return duration
		else:
			return "1.0"
	else:
		print("new")
		print(benchmark)
		return str(benchmark)



def write_midi(generated_harmony, generated_durations, key, song_name):
	offset = 0
	output_chords = []
	output_notes = []
	# create note and chord objects based on the values generated by the model
	for i, nt in enumerate(generated_harmony):
		rn = roman.RomanNumeral(nt, key)

		gen_note = None
		if i == 0:
			gen_note = note.Note()
			gen_note.pitch = rn.pitches[0]
		else:
			gen_note = note.Note()
			gen_note.pitch = get_best_note(rn.pitches, output_chords[-1])

		# pattern is a chord
	#	new_chord = chord.Chord(rn.pitches)
		gen_note.offset = offset
		gen_note.duration.quarterLength = float(generated_durations[i])
		output_notes.append(gen_note)
		output_chords.append(rn.pitches)
		offset = offset + float(generated_durations[i])


		# increase offset each iteration so that notes do not stack
		#duration = choice(durationOptions, 1, p=durationProbs)

	midi_stream = stream.Stream()
	midi_stream.append(instrument.Piano())
	midi_stream.append(output_notes)
	measures = midi_stream.makeMeasures(inPlace=False)

	new_chords = []
	for i, measure in enumerate(measures):
		if i % 2 == 0:
			measure_offset = measure.offset

			measure_notes = measure.notes
			#transpose notes down an octave
			for mnote in measure_notes:
				mnote.octave = mnote.octave - 2
			if len(measure_notes) > 0:
				measure_offset = (i+1)*4
				new_chord = chord.Chord(measure_notes)
				new_chord.duration.quarterLength = 4.0
				#if newChord.isConsonant():
				new_chord.offset= measure_offset
				new_chords.append(new_chord)

	for chord_item in new_chords:
		midi_stream.insert(chord_item)
	

	bass_line = []
	for i, nt in enumerate(output_notes):
		gen_note = note.Note()

		gen_note.octave = nt.octave - 2
		gen_note.name = nt.name
		gen_note.duration.quarterLength = nt.duration.quarterLength 
		gen_note.offset = nt.offset
		bass_line.append(gen_note)

	bass_midi = stream.Stream()
	bass_midi.append(instrument.Bass())
	bass_midi.append(bass_line)




def generate(sequence_model_name, duration_model_name, harmony_model_name, n_sections, key, sequence_len, song_name, n_mes=2):
	sections = []
	i=1
	for i in range(len(original_offsets)):
		start = offsets[i]
		end =  offsets[i]+ 4 * n_mes
		measure_durations = []
		measure_harmony = []
		for j, item in enumerate(offsets):
			if item >= start and item < end:
				if generated_duration_floats[j] + offsets[j] > end:
					new_dur = end - offsets[j]
					measure_durations.append(float(new_dur))
					measure_harmony.append(generated_harmony[j])

				if  j != len(offsets) - 1:
					if offsets[j] + generated_duration_floats[j] < end and offsets[j+1] > end:
						measure_durations.append(end - offsets[j])
						measure_harmony.append(generated_harmony[j])

					else:
						measure_durations.append(float(generated_duration[j]))
						measure_harmony.append(generated_harmony[j])

		sections.append({'durations': measure_durations, 'harmony': measure_harmony})


	diversity_ranked_sections = sorted(sections, key=lambda k: len(set(k['durations']))+len(set(k['harmony'])), reverse=True)
	complexity_bound = n_mes * 4 *10 
#	diversity_ranked_sections = [item for item in diversity_ranked_sections if len(item['durations']) < complexity_bound]

	sequence_map = {}

	sorted_freq = sorted(set(sequence), key = sequence.count)

	print('Len sorted freq:', len(sorted_freq))
	print('len diversity ranked:', len(diversity_ranked_sections))

	for i, item in enumerate(sorted_freq):
		sequence_map[item] = diversity_ranked_sections[i]




	new_duration = []
	new_harmony = []
	#build new midi
	for i in range(n_sections):
		seq_assign = sequence_map[sequence[i]]
		new_duration += seq_assign['durations']
		new_harmony += seq_assign['harmony']


	output = write_midi(new_harmony, new_duration, key, song_name)


	return output


if __name__ == '__main__':

	note_obj = note.Note('G2')
	print(note_obj.pitch.ps)

	sequence_model_name = "may4"
	key = "C"
	instrument_map = {
		"piano": {
			"duration": "duration_test_piano",
			"harmony":  "harmony_test_piano"
		},
		"bass": {
			"duration": "duration_test_piano",
			"harmony":  "harmony_test_piano"
		}
	}


	builder = SongBuilder(sequence_model_name, instrument_map, key, 25, 2)
	builder.build_instrument_part("piano")
	#builder.build_instrument_part("bass")
	builder.write_midi("teagan.midi")






