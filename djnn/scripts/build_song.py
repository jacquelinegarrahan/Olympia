from data.song import Song
from music21 import roman, stream, note
from src.utils import get_project_root
from keras.models import model_from_json
import json
import numpy
from keras.utils import np_utils
import copy
ROOT_DIR = get_project_root()


def loadModel(modelName, modelType):
	modelFile = ROOT_DIR + '/files/models/' + modelType + '/model_' + modelName + '.json'
	weightFile = ROOT_DIR + '/files/models/' + modelType + '/weights_' + modelName + '.h5'

	# load json and create model
	json_file = open(modelFile, 'r')
	loaded_model_json = json_file.read()
	json_file.close()
	loaded_model = model_from_json(loaded_model_json)

	# load weights into new model
	loaded_model.load_weights(weightFile)

	return loaded_model


def convertNotes(inputs, noteMap):
	notes = []
	for input in inputs:
		idx = numpy.argmax(input)
		result = list(noteMap.keys())[list(noteMap.values()).index(idx)]
		notes.append(result)
	return notes


def convertDuration(durations, durationMap):
	durs = []
	for input in durations:
		idx = numpy.argmax(input)
		result = list(durationMap.keys())[list(durationMap.values()).index(idx)]
		durs.append(result)
	return durs


def loadMapping(harmonyModelName, durationModelName):
	harmonyMap =  json.loads(open(ROOT_DIR + '/files/mappings/' + harmonyModelName + '_harmony.json').read())
	durationMap = json.loads(open(ROOT_DIR + '/files/mappings/' + durationModelName + '_durations.json').read())
	return harmonyMap, durationMap

def checkDuration(durationVal, durationMap, generatedDurations):

	#idx = 
	#benchmark = sum(generatedDurations) % 4 
	#newBenchmark = (sum(generatedDurations) + newDuration) % 4
	#if newBenchmark > benchmark
	idx = numpy.argmax(durationVal)

	duration = list(durationMap.keys())[list(durationMap.values()).index(idx)]
	print(duration)
	return duration



def writeMidi(generatedHarmony, generatedDurations, key, songName):
	offset = 0
	outputNotes = []
	# create note and chord objects based on the values generated by the model
	for i, nt in enumerate(generatedHarmony):
		rn = roman.RomanNumeral(nt, key)

		genNote = None
		if i == 0:
			genNote = note.Note()
			genNote.pitch = rn.pitches[0]
		else:
			genNote = note.Note()
			genNote.pitch = getBestNote(rn.pitches, outputNotes[-1])

		# pattern is a chord
	#	new_chord = chord.Chord(rn.pitches)
		genNote.offset = offset
		genNote.duration.quarterLength = float(generatedDurations[i])
		outputNotes.append(genNote)
		offset = offset + float(generatedDurations[i])

		# increase offset each iteration so that notes do not stack
		#duration = choice(durationOptions, 1, p=durationProbs)

	midi_stream = stream.Stream(outputNotes)
	saveFile = ROOT_DIR + '/files/songs/' + songName

	midi_stream.write('midi', fp=saveFile)


def getBestNote(pitches, lastNote):
	#lastPs = lastNote.ps
	return pitches[0]


def generateStartSequence(sequenceLen, mapping):
	start = []
	nOptions = len(mapping)
	for i in range(sequenceLen):
		start.append(numpy.random.choice(nOptions))
	start = np_utils.to_categorical(start, num_classes=len(mapping))
	return start


def generate(durationModelName, harmonyModelName, nNotes, key, sequenceLen, songName):
	harmonyModel = loadModel(harmonyModelName, 'harmony')
	durationModel = loadModel(durationModelName, 'duration')

	noteMap, durationMap  = loadMapping(harmonyModelName, durationModelName)

	harmonyStart = generateStartSequence(sequenceLen, noteMap)
	durationStart = generateStartSequence(sequenceLen, durationMap)

	harmonySequence = numpy.reshape(harmonyStart, (1, sequenceLen, len(noteMap)))
	durationSequence = numpy.reshape(durationStart, (1, sequenceLen, len(durationMap)))

	generatedHarmony = convertNotes(harmonySequence, noteMap)
	generatedDuration = convertDuration(durationSequence, durationMap)

	for note in range(nNotes):
		harmonicInput = copy.deepcopy(harmonySequence)
		harmonyVal = harmonyModel.predict(harmonySequence, verbose=0)
		harmonyIdx = numpy.argmax(harmonyVal)

		harmony = list(noteMap.keys())[list(noteMap.values()).index(harmonyIdx)]
		generatedHarmony.append(harmony)

		#process harmony
		nextHarmony =  np_utils.to_categorical([harmonyIdx], num_classes=len(noteMap))
		nextHarmony = numpy.reshape(nextHarmony, (1, 1, len(noteMap)))
		nextHarmony = nextHarmony/len(noteMap)
		harmonySequence = numpy.concatenate((harmonySequence, nextHarmony), axis = 1)
		harmonySequence = numpy.delete(harmonySequence, 0, axis=1)

		#process duration

		durationInput = copy.deepcopy(durationSequence)
		durationVal = durationModel.predict(durationSequence, verbose=0)

		duration = checkDuration(durationVal, durationMap, generatedDuration)
		generatedDuration.append(duration)
		nextDuration =  np_utils.to_categorical([durationMap[duration]], num_classes=len(durationMap))
		nextDuration = numpy.reshape(nextDuration, (1, 1, len(durationMap)))
		nextDuration = nextDuration/len(durationMap)
		durationSequence = numpy.concatenate((durationSequence, nextDuration), axis = 1)
		durationSequence = numpy.delete(durationSequence, 0, axis=1)

	output = writeMidi(generatedHarmony, generatedDuration, key, songName)

	return output


if __name__ == '__main__':
	durationModelName = 'allTest_duration'
	harmonyModelName =  'allTest_harmony'
	nNotes = 300
	key = 'D'
	sequenceLen = 24
	songName = 'hello1.mid'
	generate(durationModelName, harmonyModelName, nNotes, key, sequenceLen, songName)













