import logging
import numpy as np
from typing import List
from olympia import files, utils
from olympia.data import song
from olympia.models import lstm
from olympia import ROOT_DIR
from olympia.train import ModelSettings

logger = logging.getLogger("olympia")
logging.basicConfig(level=logging.DEBUG, format="%(message)s")


# CLASS: SequenceModel
# DESCRIPTION: Pulls sequence progressions from song objects and trains
# models on the progressions.
# Currently uses an LSTM model for training
# The sequences are constructed by clustering on similar measures
class SequenceModel:
    def __init__(
        self, song_objs: List[song.Song], model_settings: ModelSettings
    ) -> None:
        self.settings = model_settings
        self.model_hash = utils.get_model_hash(model_settings)
        self.songs = song_objs
        self.sequences = []
        self.inputs = []
        self.outputs = []
        self.mapping = None
        self.settings = model_settings.dict()

        self.get_all_sequences()
        self.prepare_sequences()

    # METHOD: get_all_sequences
    # DESCRIPTION: kicks off clustering on sequences and returns a map of the clusters to the measures
    def get_all_sequences(self):
        for song_obj in self.songs:
            sequence = song_obj.get_cluster_sequence(
                n_mes=self.settings.n_measures, n_clusters=self.settings.n_clusters
            )

            if np.var(sequence) / np.mean(sequence) > 1:
                self.sequences.append(sequence)

    # METHOD: prepare_sequences
    # DESCRIPTION: prepare sequences for the lstm model
    def prepare_sequences(self):
        self.inputs, self.outputs = lstm.build_lstm_input_output(
            self.settings.sequence_length,
            None,
            self.sequences,
            n_clusters=self.settings.n_clusters,
        )

    # METHOD: train_sequences
    # DESCRIPTION: kick off sequence training and return the trained model
    def train_sequences(self):
        self.model = lstm.train_lstm(self)
        self.score = lstm.check_output_diversity(self)

    # METHOD: save_model
    # DESCRIPTION: save model to db and s3
    def save_model(self):
        files.save_model(self.model, self.model_hash, self.settings.dict(), self.score)
