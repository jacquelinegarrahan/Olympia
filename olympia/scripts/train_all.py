from pydantic import BaseModel
from djnn.train import duration, harmony, sequence



class ModelSettings(BaseModel):
	# neural models
	sequence_length: int = 20
	epochs: int = 100

class HarmonySettings(ModelSettings):
	model_type: str = "harmony"

class DurationSettings(ModelSettings):
	model_type: str = "duration"

class SequenceSettings(ModelSettings):
	model_type: str = "sequence"
	n_clusters: int = 15
	n_measures: int = 50


def train_all(midi_dir, model_name, sequence_len, epochs):
	sequence_model = sequence.SequenceModel()
	sequence_model.train_sequences(epochs)

	harmony_model = harmony.HarmonyModel()
	harmony_model.train_harmony(epochs)

	duration_model = duration.DurationModel()
	duration_model.train_duration(epochs)



if __name__ == '__main__':
	midi_dir = 'small_test'
	model_name = 'class_test'

	song_objs = song.get_all_songs(midi_dir)
	harmony_model = SequenceModel(song_objs, n_clusters, n_measures, sequence_len, midi_dir, model_name)
	harmony_model.train_sequences(5)

	song_objs = song.get_all_songs(midi_dir)
	harmony_model = HarmonyModel(song_objs, sequence_len, midi_dir, model_name, instrument="bass")
	harmony_model.train_harmony(epochs)

	song_objs = song.get_all_songs(midi_dir)
	dur_model = DurationModel(song_objs, sequence_len, midi_dir, model_name, instrument="piano")
	dur_model.train_duration(epochs)
