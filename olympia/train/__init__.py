from datetime import datetime
from pydantic import BaseModel
from typing import List
from abc import ABC, abstractmethod
from olympia import files, utils
from olympia.models import lstm
from olympia.data import song


class ModelSettings(BaseModel):
    # neural models
    model_type: str = None
    sequence_length: int = 6
    epochs: int = 100
    instrument: str = "piano"
    n_clusters: int = 15
    n_measures: int = 2
    create_date: str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    hidden_layer: int = 25
    epochs: int = 1000
    learning_rate: float = 0.3


class Model(ABC):
    def __init__(
        self, song_objs: List[song.Song], model_settings: ModelSettings
    ) -> None:
        self.settings = model_settings
        self.hash = utils.get_model_hash(model_settings)
        self.songs = song_objs
        self.mapping = {}

        self.inputs = []
        self.outputs = []

    # METHOD: train_sequences
    # DESCRIPTION: kick off sequence training and return the trained model
    def train(self):
        self.model = lstm.train_lstm(self)
        self.score = lstm.check_output_diversity(self)

    # METHOD: save_model
    # DESCRIPTION: save model to db and s3
    def save(self):
        files.save_model(self.model, self.hash, self.settings.dict(), self.score)
        # save mapping
        if self.mapping:
            files.save_mapping(self.mapping, self.hash)

    @abstractmethod
    def prepare_input(self):
        pass
