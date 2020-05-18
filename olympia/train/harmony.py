import logging
from typing import List
from olympia import files, utils
from olympia.data import song
from olympia.models import lstm
from olympia.train import ModelSettings
from olympia import ROOT_DIR

logger = logging.getLogger("olympia")
logging.basicConfig(level=logging.DEBUG, format="%(message)s")

# CLASS: HarmonyModel
# DESCRIPTION: Pulls harmonic progressions from song objects and trains
# models on the progressions.
# Currently uses an LSTM model for training
class HarmonyModel:
    def __init__(
        self, song_objs: List[song.Song], model_settings: ModelSettings
    ) -> None:
        self.settings = ModelSettings(model_settings)
        self.model_hash = utils.get_model_hash(model_settings)
        self.songs = song_objs
        self.harmonies = []
        self.inputs = []
        self.outputs = []
        self.mapping = None
        self.model = None

        # prepare model for training
        self.get_all_harmonies(instrument=model_settings.instrument)
        self.build_harmony_map()
        self.prepare_input()

    # METHOD: get_all_harmonies
    # DESCRIPTION: get harmonic progressions for each song in model
    # if instrument is given, this will only include matching parts
    def get_all_harmonies(self, instrument=None):
        # filter durations by instrument

        if not instrument:
            for song_obj in self.songs:
                for part in song_obj.parts:
                    self.harmonies.append(part.pitches)

        else:
            for song_obj in self.songs:
                part = song_obj.get_part_by_instrument(instrument)
                if part:
                    self.harmonies.append(part.pitches)

    # METHOD: build_harmony_map
    # DESCRIPTION: build a mapping of note jumps to an integer
    def build_harmony_map(self):
        unique_harmonies = []

        for progression in self.harmonies:
            for item in progression:
                if item not in unique_harmonies:
                    unique_harmonies.append(item)

        mapping = dict((item, dur) for dur, item in enumerate(unique_harmonies))
        self.mapping = mapping

        # save mapping
        files.save_mapping(mapping, self.model_hash)

    # METHOD: prepare_sequences
    # DESCRIPTION: prepare sequences for the lstm model
    def prepare_input(self):
        self.inputs, self.outputs = lstm.build_lstm_input_output(
            self.settings.sequence_length, self.mapping, self.harmonies
        )

    # METHOD: train_harmony
    # DESCRIPTION: kick off harmony training and return the trained model
    def train_harmony(self):
        self.model = lstm.train_lstm(self, key=self.key, notes=True)
        self.score = lstm.check_output_diversity(self)

    # METHOD: save_model
    # DESCRIPTION: save model to db and s3
    def save_model(self):
        files.save_model(self.model, self.model_hash, self.settings.dict(), self.score)
