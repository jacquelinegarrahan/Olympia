import logging
from typing import List
from olympia.data import song
from olympia.models import lstm
from olympia.train import ModelSettings, Model
from olympia import ROOT_DIR

logger = logging.getLogger("olympia")
logging.basicConfig(level=logging.DEBUG, format="%(message)s")


# CLASS: HarmonyModel
# DESCRIPTION: Pulls harmonic progressions from song objects and trains
# models on the progressions.
# Currently uses an LSTM model for training
class HarmonyModel(Model):
    def __init__(
        self, song_objs: List[song.Song], model_settings: ModelSettings
    ) -> None:
        super(HarmonyModel, self).__init__(song_objs, model_settings)

        # prepare model for training
        self.prepare_input()

    # METHOD: prepare_sequences
    # DESCRIPTION: prepare sequences for the lstm model
    def prepare_input(self):
        # get harmonic progressions for each song in model
        # filter durations by instrument
        harmonies = []
        if not self.settings.instrument:
            for song_obj in self.songs:
                for part in song_obj.parts:
                    harmonies.append(part.pitches)
        else:
            for song_obj in self.songs:
                part = song_obj.get_part_by_instrument(self.settings.instrument)
                if part:
                    harmonies.append(part.pitches)

        # build a mapping of note jumps to an integer
        unique_harmonies = []
        for progression in self.harmonies:
            for item in progression:
                if item not in unique_harmonies:
                    unique_harmonies.append(item)

        self.mapping = dict((item, dur) for dur, item in enumerate(unique_harmonies))

        self.inputs, self.outputs = lstm.build_lstm_input_output(
            self.settings.sequence_length, self.mapping, harmonies
        )
