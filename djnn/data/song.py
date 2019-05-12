from music21 import converter, corpus, instrument, midi, note, chord, pitch, roman, stream
import matplotlib.pyplot as plt
import matplotlib.lines as mlines

class Song():

	def __init__(self, raw_path, title=None, artist=None):
		self.title = title
		self.artist = artist
		self.raw_path = raw_path
		self.instruments = None
		self.expected_key = None
		self.time_signature = None
		self.harmonic = None
		self.roman_numerals = None
		self.duration_progression = None
		self.load_midi()

	def load_midi(self, remove_drums=True):
		mf = midi.MidiFile()
		mf.open(self.raw_path)
		mf.read()
		mf.close()
		if (remove_drums):
			for i in range(len(mf.tracks)):
				mf.tracks[i].events = [ev for ev in mf.tracks[i].events if ev.channel != 10]

		self.midi = midi.translate.midiFileToStream(mf)
		self.get_instruments()
		self.get_expected_key()
		self.get_time_signatures()
		self.get_harmonic_reduction()
		self.convert_harmonic_to_roman_numerals()
		self.get_duration_progression()

	def get_instruments(self):
		instruments = []
		part_stream = self.midi.parts.stream()
		for p in part_stream:
			aux = p
			instruments.append(p.partName)

		self.instruments = instruments 
		return instruments
		
	def getPartByInstrument(self, instrument):
		part_stream = self.midi.parts.stream()
		print("List of instruments found on MIDI file:")
		for p in part_stream:
			if p.partName == instrument:
				return p
	
	def extract_notes(self, part):
		parent_element = []
		ret = []
		for nt in part.flat.notes:        
			if isinstance(nt, note.Note):
				ret.append(max(0.0, nt.pitch.ps))
				parent_element.append(nt)
			elif isinstance(nt, chord.Chord):
				for pitch in nt.pitches:
					ret.append(max(0.0, pitch.ps))
					parent_element.append(nt)
		
		return ret, parent_element

	def get_expected_key(self):
		self.expected_key = self.midi.analyze('key')
		return self.expected_key

	def get_time_signatures(self):
		time_signature = self.midi.getTimeSignatures()[0]
		self.time_signature = '{}/{}'.format(time_signature.beatCount, time_signature.denominator)
		return self.time_signature

	def get_harmonic_reduction(self):
		ret =[]
		try:
			temp_midi = stream.Score()
			temp_midi_chords = self.midi.chordify()
			temp_midi.insert(0, temp_midi_chords)
			max_notes_per_chord = 4 
			for measure in temp_midi_chords.measures(0, None): # None = get all measures.
				if (type(measure) != stream.Measure):
					continue
					
				# count all notes length in each measure,
				# get the most frequent ones and try to create a chord with them.
				count_dict = dict()
				bass_note = note_count(measure, count_dict)
				if (len(count_dict) < 1):
					ret.append("-") # Empty measure
					continue
					
				sorted_items = sorted(count_dict.items(), key=lambda x:x[1])
				sorted_notes = [item[0] for item in sorted_items[-max_notes_per_chord:]]
				measure_chord = chord.Chord(sorted_notes)
					
				ret.append(measure_chord)

			self.harmonic = ret
		except:
			print('CHORDIFY ERROR! {}'.format(self.raw_path))
			self.harmonic = []
		return ret
	
	def convert_harmonic_to_roman_numerals(self):
		ret = []
		for c in self.harmonic:
			if c == '-':
				ret.append('-')
			else:
				roman_numeral = roman.romanNumeralFromChord(c, self.expected_key)
				ret.append(simplify_roman_name(roman_numeral))
		self.roman_numerals = ret
		return ret

	def get_duration_progression(self):
		durations = []
		parts = []
		allowed_durations = ['Acoustic Bass', 'Guitar', 'Fretless Bass', 'Harmonica', 'Piano', 'Saxophone', 'Baritone Saxophone',\
			 'Tenor Saxophone', 'Harpischord', 'Electric Bass', 'Organ', 'Electric Guitar', 'Electric Organ', 'Violin', 'Timpani',\
				 'StringInstrument', 'Clarinet', 'Brass', 'Marimba', 'Clavichord']

		for part in self.midi.parts:
			if part.partName in allowed_durations:
				parts.append(part)

		for i in range(len(parts)):
			top = parts[i].flat.notes                  
			y, parent_element = self.extract_notes(top)
			for nt in parent_element:
				try:
					if nt.duration.quarterLength < 4 :
						durations.append(float(nt.duration.quarterLength))
				except:
					pass

		self.duration_progression = durations
		return durations

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
	

def note_count(measure, count_dict):
    bass_note = None
    for chord in measure.recurse().getElementsByClass('Chord'):
        # All notes have the same length of its chord parent.
        note_length = chord.quarterLength
        for note in chord.pitches:          
            # If note is "C5", note.name is "C". We use "C5"
            # style to be able to detect more precise inversions.
            note_name = str(note) 
            if (bass_note is None or bass_note.ps > note.ps):
                bass_note = note
                
            if note_name in count_dict:
                count_dict[note_name] += note_length
            else:
                count_dict[note_name] = note_length
        
    return bass_note
                
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
	

#def removeConsecutiveFifths()


if __name__ == '__main__':
	filepath = 'test_midis/coldplay-clocks_version_2.mid'
	song = Song(filepath, 'Clocks', 'Coldplay')
	print(song.convert_harmonic_to_roman_numerals())
	song.plot_parts()
	#timeSignature.beatCount, timeSignature.denominator
