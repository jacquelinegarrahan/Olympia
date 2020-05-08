import torch
from torch import nn
import numpy as np
import logging
from random import choice
from sklearn.preprocessing import OneHotEncoder
from olympia import utils
from olympia.models import rules

logger = logging.getLogger("olympia")
logging.basicConfig(level=logging.DEBUG, format="%(message)s")


# METHOD: build_lstm_input_output
# DESCRIPTION: prepares inputs and outputs from song data
# Song data is recorded as a list of lists, so need to parse each list
# Mapping is the mapping of integer to song data type (C -> 1 etc.)
def build_lstm_input_output(sequence_length, mapping, data, min_distinct_values=8, n_clusters=None):

    # preparing input and output dataset
    X = []
    Y = []

    encoder = OneHotEncoder(handle_unknown="ignore")

    # fit the encoder to the integers used in the mapping
    # format to fit encoder
    # if a sequence model, no mapping needed beyond range
    if not mapping:
        mapping_values = [[i] for i in range(n_clusters)]

    else:
        mapping_values = [[item] for item in list(mapping.values())]

    encoder.fit(mapping_values)

    # iterate over lists
    for item in data:

        # check that at least one sequence in set and that the set is sufficiently diverse
        if len(item) > sequence_length and len(set(item)) >= min_distinct_values:

            # prepare the progression data
            prog_input = []

            for i in range(0, len(item) - sequence_length, 1):
                item_in = item[i : i + sequence_length]
                item_out = item[i + sequence_length]

                # if this is a sequence model, we have integers so don't need to map to them
                if not mapping:
                    prog_input.append([[item] for item in item_in])
                    Y.append(item_out)

                else:
                    prog_input.append([[mapping[item]] for item in item_in])
                    Y.append(mapping[item_out])

            if prog_input:

                # convert input to categorical
                for i, prog in enumerate(prog_input):
                    X.append(encoder.transform(prog).toarray())

    # reshape arrays
    n_sequences = len(X)
    if not mapping:
        X = np.reshape(X, (n_sequences, sequence_length, n_clusters))
    else:
        X = np.reshape(X, (n_sequences, sequence_length, len(mapping)))
    Y = np.array(Y)

    return X, Y


# METHOD: generate_random_input
# DESCRIPTION: generate random input sequences from available values
def generate_random_input(sequence_length, mapping, n_clusters=None, n_samples=200):

    random_X = []
    encoder = OneHotEncoder(handle_unknown="ignore")

    # fit the encoder to the integers used in the mapping
    # format to fit encoder
    # if a sequence model, no mapping needed beyond range
    if not mapping:
        mapping_values = [[i] for i in range(n_clusters)]

    else:
        mapping_values = [[item] for item in list(mapping.values())]

    encoder.fit(mapping_values)

    for i in range(n_samples):
        prog = [choice(mapping_values) for j in range(sequence_length)]
        # one hot encode input
        random_X.append(encoder.transform(prog).toarray())

    n_sequences = len(random_X)
    if not mapping:
        random_X = np.reshape(random_X, (n_sequences, sequence_length, n_clusters))
    else:
        random_X = np.reshape(random_X, (n_sequences, sequence_length, len(mapping)))

    return random_X


class LSTM(nn.Module):
    def __init__(self, input_dim, hidden_dim, layer_dim, output_dim):
        super(LSTM, self).__init__()
        # Hidden dimensions
        self.hidden_dim = hidden_dim

        # Number of hidden layers
        self.layer_dim = layer_dim

        # Building your LSTM
        # batch_first=True causes input/output tensors to be of shape
        # (batch_dim, seq_dim, feature_dim)
        self.lstm = nn.LSTM(input_dim, hidden_dim, layer_dim, batch_first=True)

        # Readout layer
        self.fc = nn.Linear(hidden_dim, output_dim)

    def forward(self, x):
        # Initialize hidden state with zeros
        h0 = torch.zeros(self.layer_dim, x.size(0), self.hidden_dim).requires_grad_()

        # Initialize cell state
        c0 = torch.zeros(self.layer_dim, x.size(0), self.hidden_dim).requires_grad_()

        # 28 time steps
        # We need to detach as we are doing truncated backpropagation through time (BPTT)
        # If we don't, we'll backprop all the way to the start even after going through another batch
        out, (hn, cn) = self.lstm(x, (h0.detach(), c0.detach()))

        # Index hidden state of last time step
        # out.size() --> 100, 28, 100
        # out[:, -1, :] --> 100, 100 --> just want last time step hidden states!
        out = self.fc(out[:, -1, :])
        # out.size() --> 100, 10
        return out


# METHOD: train_lstm
# DESCRIPTION: set up and train an lstm model
def train_lstm(builder, key=None, notes=False):

    # build appropriate model, use n_clusters for sequential and mapping for others
    if builder.mapping:
        model = LSTM(len(builder.mapping), builder.hidden_layer, 2, len(builder.mapping))
    else:
        model = LSTM(builder.n_clusters, builder.hidden_layer, 2, builder.n_clusters)

    if notes:
        criterion = rules.TheoryLoss(key)
    else:
        criterion = torch.nn.CrossEntropyLoss()
    optimizer = torch.optim.SGD(model.parameters(), lr=builder.learning_rate)

    train_input = torch.from_numpy(builder.inputs).float()
    train_output = torch.from_numpy(builder.outputs).long()

    losses = []
    converged = False
    epoch = 0

    # train until converged
    while not converged and epoch < builder.epochs:
        # make sure in train mode
        model.train()

        epoch += 1
        y_pred = model(train_input)

        loss = criterion(y_pred, train_output)

        optimizer.zero_grad()
        model.zero_grad()

        # loss.backward()

        optimizer.step()

        # get accuracy
        correct = 0
        preds = []
        for i, pred in enumerate(torch.max(y_pred.data, 1)[1]):
            if pred.item() == train_output[i].item():
                correct += 1
                preds.append(pred.item())
        logger.debug("Y : %s", preds)
        logger.debug("TRAINING EPOCH: %s", epoch)
        logger.debug("TRAIN ACCURACY: %s", correct / len(train_input))
        logger.debug("LOSS: %s", loss)

    return model


# METHOD: generate_random_output
# DESCRIPTION: generate random input and get output
def generate_random_output(builder, n_samples=200):
    random_X = generate_random_input(
        builder.sequence_length, builder.mapping, n_clusters=builder.n_clusters, n_samples=n_samples
    )

    builder.model.eval()
    X = torch.from_numpy(random_X).float()

    y_pred = builder.model(X)

    outputs = []
    for pred in torch.max(y_pred.data, 1)[1]:
        outputs.append(pred.item())

    return outputs


# METHOD: check_output_diversity
# DESCRIPTION: generates a random sequence of possible values and scores the output by the index of dispersion of the output
# We use index of dispersion because it allows us to relate scores across different means
def check_output_diversity(builder):
    outputs = generate_random_output(builder)

    return utils.get_iod(outputs)


if __name__ == "__main__":
    mapping = {"A": 1, "B": 2, "C": 3}
    print(generate_random_input(12, mapping, n_clusters=None, n_samples=200))
