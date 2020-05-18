import logging
import numpy as np

from typing import List
from olympia import files, utils
from olympia.data import song
from olympia.models import lstm
from olympia import ROOT_DIR
from olympia.train import ModelSettings, Model

logger = logging.getLogger("olympia")
logging.basicConfig(level=logging.DEBUG, format="%(message)s")


# CLASS: SequenceModel
# DESCRIPTION: Pulls sequence progressions from song objects and trains
# models on the progressions.
# Currently uses an LSTM model for training
# The sequences are constructed by clustering on similar measures
class SequenceModel(Model):
    def __init__(
        self, song_objs: List[song.Song], model_settings: ModelSettings
    ) -> None:
        super(SequenceModel, self).__init__(song_objs, model_settings)
        self.prepare_input()

    # METHOD: prepare_input
    # DESCRIPTION: prepare sequences for the lstm model
    # overrides the prepare input abstract method
    def prepare_input(self) -> None:
        for song_obj in self.songs:
            sequence = song_obj.get_cluster_sequence(
                n_mes=self.settings.n_measures, n_clusters=self.settings.n_clusters
            )

            if np.var(sequence) / np.mean(sequence) > 1:
                self.sequences.append(sequence)

        self.inputs, self.outputs = lstm.build_lstm_input_output(
            self.settings.sequence_length,
            None,
            self.sequences,
            n_clusters=self.settings.n_clusters,
        )
