from datetime import datetime
from pydantic import BaseModel


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
