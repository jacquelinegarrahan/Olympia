from pydantic import BaseModel
import hashlib
import json
from datetime import datetime
from olympia.train import duration, harmony, sequence, ModelSettings
from olympia.data import song


def train_model(song_objs, settings=None, run_duration=False, run_sequence=False, run_harmony=False):

    model_settings = None
    if settings:
        model_settings = ModelSettings(**settings)

    else:
        model_settings = ModelSettings()

    if run_sequence:
        sequence_model = sequence.SequenceModel(song_objs, model_settings)
        sequence_model.train_sequences()

    if run_harmony:
        harmony_model = harmony.HarmonyModel(song_objs, model_settings)
        harmony_model.train_harmony()

    if run_duration:
        duration_model = duration.DurationModel(song_objs, model_settings)
        duration_model.train_duration()


if __name__ == "__main__":
    settings = {"instrument": "piano", "time_signature": "4/4", "epochs": 5000}
    song_objs = song.get_songs("piano", time_signature="4/4", key=None, limit=10)
    train_model(song_objs, run_sequence=True)
