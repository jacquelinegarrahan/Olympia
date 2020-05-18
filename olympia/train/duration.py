import logging
from typing import List
from pydantic import BaseModel
from olympia.models import lstm
from olympia.data import song
from olympia import files, utils
from olympia import ROOT_DIR
from olympia.train import ModelSettings


logger = logging.getLogger("olympia")
logging.basicConfig(level=logging.DEBUG, format="%(message)s")


# CLASS: DurationModel
# DESCRIPTION: Pulls duration progressions from song objects and trains
# models on the progressions.
# Currently uses an LSTM model for training
class DurationModel:
    def __init__(
        self, song_objs: List[song.Song], model_settings: ModelSettings
    ) -> None:
        self.settings = model_settings
        self.model_hash = utils.get_model_hash(model_settings)
        self.songs = song_objs
        self.mapping = {}
        self.n_clusters = None
        self.durations = []

        # prepare model for build
        self.get_all_durations()
        self.build_duration_map()
        self.prepare_input()

    # METHOD: get_all_durations
    # DESCRIPTION: pull durations for each song used in model
    def get_all_durations(self) -> None:
        # filter durations by instrument

        if not self.instrument:
            for song_obj in self.songs:
                for part in song_obj.parts:
                    self.durations.append(part.duration_progression)

        else:
            for song_obj in self.songs:
                logger.debug("getting duration for %s", song_obj.raw_path)
                part = song_obj.get_part_by_instrument(self.instrument)
                if part:
                    self.durations.append(part.duration_progression)

        self.n_training_notes = sum([len(x) for x in self.durations])

    # METHOD: build_duration_map
    # DESCRIPTION: build a mapping of music21 midi duration to an integer
    def build_duration_map(self) -> None:
        unique_durations = []

        for progression in self.durations:
            for item in progression:
                if item not in unique_durations:
                    unique_durations.append(item)

        mapping = dict((item, dur) for dur, item in enumerate(unique_durations))
        self.mapping = mapping

        # save mapping
        files.save_mapping(mapping, self.model_hash)

    # METHOD: prepare_sequences
    # DESCRIPTION: prepare sequences for the lstm model
    def prepare_input(self) -> None:
        self.inputs, self.outputs = lstm.build_lstm_input_output(
            self.settings.sequence_length,
            self.mapping,
            self.durations,
            min_distinct_values=3,
        )

    # METHOD: train_duration
    # DESCRIPTION: kick off duration training and return the trained model
    def train_duration(self) -> None:
        self.model = lstm.train_lstm(self)
        self.score = lstm.check_output_diversity(self)

    # METHOD: save_model
    # DESCRIPTION: save model to db and s3
    def save_model(self) -> None:
        files.save_model(self.model, self.model_hash, self.settings.dict(), self.score)
