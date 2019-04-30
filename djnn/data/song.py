from music21 import converter, corpus, instrument, midi, note, chord, pitch, roman, stream
import matplotlib.pyplot as plt
import matplotlib.lines as mlines

class Song():

	def __init__(self, rawPath, title=None, artist=None):
		self.title = title
		self.artist = artist
		self.rawPath = rawPath
		self.instruments = None
		self.expectedKey = None
		self.timeSignature = None
		self.harmonic = None
		self.romanNumerals = None
		self.durationProgression = None
		self.loadMidi()

	def loadMidi(self, remove_drums=True):
		mf = midi.MidiFile()
		mf.open(self.rawPath)
		mf.read()
		mf.close()
		if (remove_drums):
			for i in range(len(mf.tracks)):
				mf.tracks[i].events = [ev for ev in mf.tracks[i].events if ev.channel != 10]

		self.midi = midi.translate.midiFileToStream(mf)
		self.getInstruments()
		self.getExpectedKey()
		self.getTimeSignatures()
		self.getHarmonicReduction()
		self.convertHarmonicToRomanNumerals()
		self.getDurationProgression()

	def getInstruments(self):
		instruments = []
		partStream = self.midi.parts.stream()
		for p in partStream:
			aux = p
			instruments.append(p.partName)

		self.instruments = instruments 
		return instruments
		
	def getPartByInstrument(self, instrument):
		partStream = self.midi.parts.stream()
		print("List of instruments found on MIDI file:")
		for p in partStream:
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

	def getExpectedKey(self):
		self.expectedKey = self.midi.analyze('key')
		return self.expectedKey

	def getTimeSignatures(self):
		timeSignature = self.midi.getTimeSignatures()[0]
		self.timeSignature = '{}/{}'.format(timeSignature.beatCount, timeSignature.denominator)
		return self.timeSignature

	def getHarmonicReduction(self):
		ret =[]
		try:
			tempMidi = stream.Score()
			tempMidiChords = self.midi.chordify()
			tempMidi.insert(0, tempMidiChords)
			maxNotesPerChord = 4 
			for measure in tempMidiChords.measures(0, None): # None = get all measures.
				if (type(measure) != stream.Measure):
					continue
					
				# count all notes length in each measure,
				# get the most frequent ones and try to create a chord with them.
				countDict = dict()
				bassNote = noteCount(measure, countDict)
				if (len(countDict) < 1):
					ret.append("-") # Empty measure
					continue
					
				sortedItems = sorted(countDict.items(), key=lambda x:x[1])
				sortedNotes = [item[0] for item in sortedItems[-maxNotesPerChord:]]
				measureChord = chord.Chord(sortedNotes)
					
				ret.append(measureChord)

			self.harmonic = ret
		except:
			print('CHORDIFY ERROR! {}'.format(self.rawPath))
			self.harmonic = []
		return ret
	
	def convertHarmonicToRomanNumerals(self):
		ret = []
		for c in self.harmonic:
			if c == '-':
				ret.append('-')
			else:
				romanNumeral = roman.romanNumeralFromChord(c, self.expectedKey)
				ret.append(simplifyRomanName(romanNumeral))
		self.romanNumerals = ret
		return ret

	def getDurationProgression(self):
		durations = []
		parts = []
		allowedDurations = ['Acoustic Bass', 'Guitar', 'Fretless Bass', 'Harmonica', 'Piano', 'Saxophone', 'Baritone Saxophone',\
			 'Tenor Saxophone', 'Harpischord', 'Electric Bass', 'Organ', 'Electric Guitar', 'Electric Organ', 'Violin', 'Timpani',\
				 'StringInstrument', 'Clarinet', 'Brass', 'Marimba', 'Clavichord']

		for part in self.midi.parts:
			if part.partName in allowedDurations:
				parts.append(part)

		for i in range(len(parts)):
			top = parts[i].flat.notes                  
			y, parent_element = self.extract_notes(top)
			for nt in parent_element:
				try:
					durations.append(float(nt.duration.quarterLength))
				except:
					pass
		self.durationProgression = durations
		return durations

	def plotOffsetVsPitch(self):
		self.midi.plot('scatter', 'offset', 'pitchClass')
	
	def plotPitchClass(self):
		self.midi.plot('histogram', 'pitchClass', 'count')

	def plotParts(self):
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
	

def noteCount(measure, count_dict):
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
                
def simplifyRomanName(roman_numeral):
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
	print(song.convertHarmonicToRomanNumerals())
	song.plotParts()
	#timeSignature.beatCount, timeSignature.denominator
