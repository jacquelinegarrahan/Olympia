from music21 import converter, corpus, instrument, midi, note, chord, pitch, roman, stream
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
import numpy as np
import glob
import boto3
from sklearn.cluster import KMeans
from sklearn.preprocessing import normalize

from djnn import ROOT_DIR


class Part():

	def __init__(self, part_obj):

		self.instrument = part_obj.partName
		self.notes = part_obj.notes
		self.notes_and_rests = part_obj.notesAndRests
		self.pitch_differences = []
		self.harmony = None
		self.roman_numerals = None
		self.duration_progression = None
		self.get_pitch_differences()
		self.chord_progression = part_obj.chordify()
		self.get_harmonic_reduction()
		self.convert_harmonic_to_roman_numerals()
		self.get_duration_progression()

	def get_pitch_differences(self):
		
		pitch_vector = []
		for note in self.notes:
			if note.isChord:
				pitch_vector.append(note[-1].pitch.ps)
			
			else:
				pitch_vector.append(note.pitch.ps)
		
		self.pitch_differences = np.diff(pitch_vector)


	def get_harmonic_reduction(self):
		reduction = []

		temp_midi = stream.Score()
		temp_midi.insert(0, self.chord_progression)
		max_notes_per_chord = 4 

		for measure in temp_midi.measures(0, None): # None = get all measures.
			if (type(measure) != stream.Measure):
				continue
					
			# count all notes length in each measure,
			count_dict = note_count(measure)
			if (len(count_dict) < 1):
				ret.append("-") # Empty measure
				continue
					
			sorted_items = sorted(count_dict.items(), key=lambda x:x[1])
			sorted_notes = [item[0] for item in sorted_items[-max_notes_per_chord:]]
			measure_chord = chord.Chord(sorted_notes)
					
			reduction.append(measure_chord)

		self.harmony = reduction
		
		return reduction
		
	def convert_harmonic_to_roman_numerals(self):
		ret = []
		for c in self.harmony:
			if c == '-':
				ret.append('-')
			else:
				roman_numeral = roman.romanNumeralFromChord(c, self.expected_key)
				ret.append(simplify_roman_name(roman_numeral))
		self.roman_numerals = ret
		return ret

	def get_duration_progression(self, prune_complex=True):
		durations = []

		for nt in self.notes:
			if nt.duration.type != "complex":
				durations.append(nt.duration.type)

		self.duration_progression = durations
		return durations


class Song():

	def __init__(self, raw_path, title=None, artist=None):
		self.title = title
		self.artist = artist
		self.raw_path = raw_path
		self.expected_key = None
		self.time_signature = None
		#self.load_midi()
		self.parts = []
		self.instruments = []

		self.load_midi()

	def load_midi(self, remove_drums=True):
		mf = midi.MidiFile()
		mf.open(self.raw_path)
		mf.read()
		mf.close()
	#	if (remove_drums):
	#		for i in range(len(mf.tracks)):
	#			mf.tracks[i].events = [ev for ev in mf.tracks[i].events if ev.channel != 10]

		self.midi = midi.translate.midiFileToStream(mf)
		self.get_parts()
		self.get_expected_key()
		self.get_time_signatures()

	def get_parts(self):
		part_stream = self.midi.parts.stream()
		for p in part_stream:
			part_obj = Part(p)
			self.parts.append(part_obj)
			self.instruments.append(part_obj.instrument)
		
	def get_part_by_instrument(self, instrument):
		for p in self.parts:
			if p.instrument and instrument in p.instrument.lower():
				return p

	def get_expected_key(self):
		self.expected_key = self.midi.analyze('key')
		return self.expected_key

	def get_time_signatures(self):
		time_signature = self.midi.getTimeSignatures()[0]
		self.time_signature = '{}/{}'.format(time_signature.beatCount, time_signature.denominator)
		return self.time_signature


	def plot_offset_vs_pitch(self):
		self.midi.plot('scatter', 'offset', 'pitchClass')
	
	def plot_pitch_class(self):
		self.midi.plot('histogram', 'pitchClass', 'count')

	def plot_parts(self):
		fig = plt.figure(figsize=(12, 5))
		ax = fig.add_subplot(1, 1, 1)
		minPitch = pitch.Pitch('C10').ps
		maxPitch = 0
		xMax = 0
		
		# Drawing notes.
		for i in range(len(self.midi.parts)):
			top = self.midi.parts[i].flat.notes                  
			y, parent_element = self.extract_notes(top)
			if (len(y) < 1): continue
				
			x = [n.offset for n in parent_element]
			ax.scatter(x, y, alpha=0.6, s=7)
			
			aux = min(y)
			if (aux < minPitch): minPitch = aux
				
			aux = max(y)
			if (aux > maxPitch): maxPitch = aux
				
			aux = max(x)
			if (aux > xMax): xMax = aux
		
		for i in range(1, 10):
			linePitch = pitch.Pitch('C{0}'.format(i)).ps
			if (linePitch > minPitch and linePitch < maxPitch):
				ax.add_line(mlines.Line2D([0, xMax], [linePitch, linePitch], color='red', alpha=0.1))            

		plt.ylabel("Note index (each octave has 12 notes)")
		plt.xlabel("Number of quarter notes (beats)")
		plt.title('Voices motion approximation, each color is a different instrument, red lines show each octave')
		plt.show()

	def get_cluster_sequence(self, n_mes=1, n_clusters=20):
		representations = []
		measures = self.midi.makeMeasures()
		measures = measures.getElementsByClass('Measure')

		measureDict = {}

		for i in range(int(len(measures)/n_mes)):
			for nt in self.notes:
				if nt.offset >= 4*i*n_mes and nt.offset < 4*n_mes*(1+i):
					if i not in measureDict:
						measureDict[i] = [nt]
					else:
						measureDict[i].append(nt)

		#iterate over measure snippets to create structure
		for i in range(int(len(measures)/n_mes)):
			if i in measureDict:
				measure_offset_rep = []
				measure_note_rep = []
				elNotes = []

				for mnote in measureDict[i]:
						if mnote.isChord:
							for cnote in mnote:
								measure_offset_rep.append(cnote.offset - 4*i*n_mes)
								measure_note_rep.append(cnote.pitch.ps)
						else:
							measure_offset_rep.append(mnote.offset - 4*i*n_mes)
							measure_note_rep.append(mnote.pitch.ps)

				if len(measure_note_rep) > 0 and len(measure_note_rep) > 0:
					representations.append([np.mean(measure_offset_rep), np.mean(measure_note_rep)])
		return get_cluster_labels(np.array(representations), n_clusters=n_clusters)
			

def note_count(measure):
	count_dict = {}
	base_note = None
	for chord in measure.recurse().getElementsByClass('Chord'):
		# All notes have the same length of its chord parent.
		note_length = chord.quarterLength
		for note in chord.pitches:          
			# If note is "C5", note.name is "C". We use "C5"
			# style to be able to detect more precise inversions.
			note_name = str(note) 
			if (base_note is None or base_note.ps > note.ps):
				base_note = note
				
			if note_name in count_dict:
				count_dict[note_name] += note_length
			else:
				count_dict[note_name] = note_length
		
	return count_dict
				
def simplify_roman_name(roman_numeral):
	# Chords can get nasty names as "bII#86#6#5",
	# in this method we try to simplify names, even if it ends in
	# a different chord to reduce the chord vocabulary and display
	# chord function clearer.
	ret = roman_numeral.romanNumeral
	inversion_name = None
	inversion = roman_numeral.inversion()
	
	# Checking valid inversions.
	if ((roman_numeral.isTriad() and inversion < 3) or
			(inversion < 4 and
				 (roman_numeral.seventh is not None or roman_numeral.isSeventh()))):
		inversion_name = roman_numeral.inversionName()
		
	if (inversion_name is not None):
		ret = ret + str(inversion_name)
		
	elif (roman_numeral.isDominantSeventh()): ret = ret + "M7"
	elif (roman_numeral.isDiminishedSeventh()): ret = ret + "o7"
	return ret



def get_cluster_labels(matrix, n_clusters=20):
	normed_matrix = normalize(matrix, axis=1, norm='l1')
	if matrix.shape[0] > n_clusters:
		kclusterer = KMeans(n_clusters=n_clusters).fit(normed_matrix)
		
		labels = kclusterer.labels_
		return labels
	else:
		return False


def get_all_songs(midi_dir):
	songs = []
	for file in glob.glob(ROOT_DIR + '/djnn/midis/' + midi_dir + "/*.mid"):
		song_obj = Song(file)
		songs.append(song_obj)
	return songs



if __name__ == '__main__':
	filepath = ROOT_DIR + '/djnn/midis/test_midis/coldplay-clocks_version_2.mid'
	song_obj = Song(filepath, 'Clocks', 'Coldplay')
	for part in song_obj.parts:
		print(part.duration_progression)
	#song_obj.load_midi()
	#print(song.parts)
	#song.get_self_similarity()
	#timeSignature.beatCount, timeSignature.denominator
