import logging
from typing import List
from pydantic import BaseModel
from olympia.data import song
from olympia import files, utils
from olympia import ROOT_DIR
from olympia.train import ModelSettings, Model
from olympia.models import lstm

logger = logging.getLogger("olympia")
logging.basicConfig(level=logging.DEBUG, format="%(message)s")


# CLASS: DurationModel
# DESCRIPTION: Pulls duration progressions from song objects and trains
# models on the progressions.
# Currently uses an LSTM model for training
class DurationModel(Model):
    def __init__(
        self, song_objs: List[song.Song], model_settings: ModelSettings
    ) -> None:
        super(DurationModel, self).__init__(song_objs, model_settings)

        # prepare model for build
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

    # METHOD: prepare_sequences
    # DESCRIPTION: prepare sequences for the lstm model
    def prepare_input(self) -> None:
        # filter durarions by instrument
        durations = []
        if not self.settings.instrument:
            for song_obj in self.songs:
                for part in song_obj.parts:
                    durations.append(part.duration_progression)

        else:
            for song_obj in self.songs:
                logger.debug("getting duration for %s", song_obj.raw_path)
                part = song_obj.get_part_by_instrument(self.settings.instrument)
                if part:
                    durations.append(part.duration_progression)

        self.n_training_notes = sum([len(x) for x in durations])

        # build mapping
        unique_durations = []
        for progression in durations:
            for item in progression:
                if item not in unique_durations:
                    unique_durations.append(item)

        mapping = dict((item, dur) for dur, item in enumerate(unique_durations))
        self.mapping = mapping

        # set up input/output
        self.inputs, self.outputs = lstm.build_lstm_input_output(
            self.settings.sequence_length,
            self.mapping,
            durations,
            min_distinct_values=3,
        )
