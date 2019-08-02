from djnn.data.song import Song
from music21 import roman, stream, note, chord, instrument
from keras.models import model_from_json
import json
import numpy
from keras.utils import np_utils
import copy
import random
from djnn import ROOT_DIR


class SongBuilder():

	def __init__(self, sequence_model_name, instrument_map, key, sequence_len):

		self.instrument_map = instrument_map
		self.sequence_model_name = sequence_model_name
		self.midi_stream = stream.Stream()
		self.key = key
		self.sequence_len = sequence_len
		self.n_notes = n_sections * n_mes * 5 # produce extra for more material
		self.sequence = self.build_sequence()

	def get_seed(self, mapping):
		#get allowed based off of key
		start = []
		n_options = len(mapping)
		for i in range(self.sequence_len):
			start.append(numpy.random.choice(n_options))
		start = np_utils.to_categorical(start, num_classes=len(mapping))
		return start

	def build_sequence(self):
		sequence_model = load_model(self.sequence_model_name, 'sequence')

		n_section_options = sequence_model.output_shape[1]
		sequence_len = sequence_model.input_shape[1]
		start = random.sample(range(0, n_section_options), sequence_len)
		sequence = np_utils.to_categorical(start, num_classes=n_section_options)
		sequence = numpy.reshape(sequence, (1, sequence_len, n_section_options))

		generated_sequence = []

		for i in range(n_sections):
			seq_input = copy.deepcopy(sequence)
			seq_val = sequence_model.predict(seq_input, verbose=0)
			seq = numpy.argmax(seq_val)

			generated_sequence.append(seq)

			next_seq =  np_utils.to_categorical([seq], num_classes=n_section_options)
			next_seq = numpy.reshape(next_seq, (1, 1, n_section_options))
			next_seq = next_seq/n_section_options
			sequence = numpy.concatenate((sequence, next_seq), axis = 1)
			sequence = numpy.delete(sequence, 0, axis=1)

		return generated_sequence


	def build_instrument_part(self, instrument)

		instrument_part = stream.Part()
		if "piano" in instrument:
			instrument_part.append(instrument.Piano())

		elif "bass" in instrument:
			instrument_part.append(instrument.Bass())

		durations = self.generate_durations(instrument)
		harmony = self.generate_harmony(instrument)

		self.midi_stream.append(instrument_part)

	def generate_harmony(self, instrument): 
		harmony_model = load_model(self.instrument_map[instrument]["harmony"], 'harmony')
		sequence_len = harmony_model.input_shape[1]
		harmony_mapping = load_mapping(self.instrument_map[instrument]["harmony"], "harmony")

		harmony_sequence = self.get_seed(harmony_mapping)
		harmony_sequence = numpy.reshape(harmony_sequence, (1, sequence_len, len(harmony_mapping)))
		generated_harmony = map_values(harmony_sequence, harmony_mapping)

		for i, note in enumerate(range(self.n_notes)):
			print('generating note %s', i)
			harmonic_input = copy.deepcopy(harmony_sequence)
			harmony_val = harmony_model.predict(harmonic_input, verbose=0)
			harmony_idx = numpy.argmax(harmony_val)

			harmony = list(note_map.keys())[list(note_map.values()).index(harmony_idx)]
			generated_harmony.append(harmony)

			#process harmony
			next_harmony =  np_utils.to_categorical([harmony_idx], num_classes=len(note_map))
			next_harmony = numpy.reshape(next_harmony, (1, 1, len(note_map)))
			next_harmony = next_harmony/len(note_map)
			harmony_sequence = numpy.concatenate((harmony_sequence, next_harmony), axis = 1)
			harmony_sequence = numpy.delete(harmony_sequence, 0, axis=1)

		return generated_harmony

	def generate_duration(self, instrument):
		#process duration
		duration_model = load_model(self.instrument_map[instrument]["duration"], 'duration')
		sequence_len = duration_model.input_shape[1]
		duration_mapping = load_mapping(self.instrument_map[instrument]["duration"], "duration")

		duration_sequence = self.get_seed_pitches(duration_mapping)
		duration_sequence = numpy.reshape(duration_sequence, (1, sequence_len, len(duration_mapping)))
		generated_duration= map_values(duration_sequence, duration_map)

		for i, note in enumerate(range(self.n_notes)):
			print('generating note %s', i)

			duration_input = copy.deepcopy(duration_sequence)
			duration_val = duration_model.predict(duration_input, verbose=0)

			duration = check_duration(duration_val, duration_map, generated_duration)
			generated_duration.append(duration)
			next_duration =  np_utils.to_categorical([duration_map[duration]], num_classes=len(duration_map))
			next_duration = numpy.reshape(next_duration, (1, 1, len(duration_map)))
			next_duration = next_duration/len(duration_map)
			duration_sequence = numpy.concatenate((duration_sequence, next_duration), axis = 1)
			duration_sequence = numpy.delete(duration_sequence, 0, axis=1)

		return generated_duration







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
		idx = numpy.argmax(input)
		result = list(note_map.keys())[list(note_map.values()).index(idx)]
		notes.append(result)
	return notes


def load_mapping(model_name, model_type):
	mapping =  json.loads(open(ROOT_DIR + '/files/mappings/' + model_name + '_' + model_type + '.json').read())
	return mapping






def check_duration(duration_val, duration_map, generated_durations):

	#idx = 
	idx = numpy.argmax(duration_val)
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


	save_file = ROOT_DIR + '/files/songs/' + song_name

	full_stream = stream.Stream()
	full_stream.insert(bass_midi)
	full_stream.insert(midi_stream)

	full_stream.write('midi', fp=save_file)


def get_best_note(pitches, last_pitches):
	new_chord_ps = [pitch.ps for pitch in pitches]
	old_chord_ps = [pitch.ps for pitch in last_pitches]
	max_len = len(new_chord_ps)
	if len(old_chord_ps) < max_len:
		max_len = len(old_chord_ps)
	
	new_chord_ps = new_chord_ps[:max_len]
	old_chord_ps = old_chord_ps[:max_len]


	dif_indices = []
	for i, ps in enumerate(new_chord_ps):
		if ps != old_chord_ps[i]:
			dif_indices.append(i)

	if len(dif_indices) == 0:
		#lastPs = lastNote.ps
		choice = random.randint(0, len(pitches)-1)
		return pitches[choice]
	else:
		return pitches[numpy.random.choice(dif_indices)]


def generate_start(sequence_len, mapping):
	start = []
	n_options = len(mapping)
	for i in range(sequence_len):
		start.append(numpy.random.choice(n_options))
	start = np_utils.to_categorical(start, num_classes=len(mapping))
	return start






def generate(sequence_model_name, duration_model_name, harmony_model_name, n_sections, key, sequence_len, song_name, n_mes=2)
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
	duration_model_name = 'subset'
	harmony_model_name =  'subset'
	sequence_model_name = 'sequence_build'
	n_sections = 50
	key = 'C'
	sequence_len = 24
	song_name = 'sequence_test5.mid'
	n_mes = 2
	generate(sequence_model_name, duration_model_name, harmony_model_name, n_sections, key, sequence_len, song_name, n_mes)













