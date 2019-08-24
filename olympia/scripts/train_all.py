from djnn.train import duration, harmony, sequence


def train_all(midi_dir, model_name, sequence_len, epochs):
	sequence_model = sequence.SequenceModel()
	sequence_model.train_sequences(epochs)

	harmony_model = harmony.HarmonyModel()
	harmony_model.train_harmony(epochs)

	duration_model = duration.DurationModel()
	duration_model.train_duration(epochs)



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

	song_objs = song.get_all_songs(midi_dir)
	harmony_model = HarmonyModel(song_objs, sequence_len, midi_dir, model_name, instrument="bass")
	harmony_model.train_harmony(epochs)

	song_objs = song.get_all_songs(midi_dir)
	dur_model = DurationModel(song_objs, sequence_len, midi_dir, model_name, instrument="piano")
	dur_model.train_duration(epochs)
