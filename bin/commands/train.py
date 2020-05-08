import click
from olympia.data import song
from olympia.train import ModelSettings
from olympia.train.duration import DurationModel
from olympia.train.sequence import SequenceModel
from olympia.train.harmony import HarmonyModel

INSTRUMENT = "guitar"
TIME_SIGNATURE = "4/4"
SONG_LIMIT = 10
TRAINING_EPOCHS = 500
SEQUENCE_LENGTH = 6
KEY = "C"


@click.group()
def train():
    pass


@train.command()
def train_duration():
    model_settings = ModelSettings(
        instrument=INSTRUMENT, sequence_length=SEQUENCE_LENGTH, model_type="duration", epochs=TRAINING_EPOCHS
    )
    songs = song.get_songs(INSTRUMENT, time_signature=TIME_SIGNATURE, limit=SONG_LIMIT)
    duration_model = DurationModel(songs, model_settings)
    duration_model.train_duration()
    duration_model.save_model()


@train.command()
def train_sequence():
    model_settings = ModelSettings(
        instrument=INSTRUMENT, sequence_length=SEQUENCE_LENGTH, model_type="sequence", epochs=TRAINING_EPOCHS
    )
    songs = song.get_songs(INSTRUMENT, time_signature=TIME_SIGNATURE, limit=SONG_LIMIT)
    sequence_model = SequenceModel(songs, model_settings)
    sequence_model.train_sequences()
    sequence_model.save_model()


@train.command()
def train_harmony():
    model_settings = ModelSettings(
        instrument=INSTRUMENT, sequence_length=SEQUENCE_LENGTH, model_type="sequence", epochs=TRAINING_EPOCHS
    )
    songs = song.get_songs(INSTRUMENT, time_signature=TIME_SIGNATURE, limit=SONG_LIMIT)
    harmony_model = HarmonyModel(songs, model_settings, KEY)
    harmony_model.train_harmony()
    harmony_model.save_model()
