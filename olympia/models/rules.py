import torch

# added all octaves for triads,
# still need to find a way
# to stop it from going over 100


# Base notes for each key
# f is flat
KEY_MAP = {
    "C": 0,
    "C#": 1,
    "Df": 1,
    "D": 2,
    "D#": 3,
    "Ef": 3,
    "E": 4,
    "F": 5,
    "F#": 6,
    "Gf": 6,
    "G": 7,
    "G#": 8,
    "Af": 8,
    "A": 9,
    "A#": 10,
    "Bf": 10,
    "B": 11,
}


# major diatonic triads
def get_major_diatonic_triads(key):
    base_note = KEY_MAP[key]
    major_diatonic_triads = [
        [base_note, base_note + 4, base_note + 7],
        [base_note + 2, base_note + 5, base_note + 9],
        [base_note + 4, base_note + 7, base_note + 11],
        [base_note + 5, base_note + 9, base_note + 12],
        [base_note + 7, base_note + 11, base_note + 14],
        [base_note + 9, base_note + 12, base_note + 16],
        [base_note + 11, base_note + 14, base_note + 17],
        [base_note + 12, base_note + 16, base_note + 19],
    ]

    # adjust based on octave
    octave_adjusted_triads = [[z + octave * 12 for z in y] for y in major_diatonic_triads for octave in range(8)]
    return octave_adjusted_triads


# natural minor diatonic triads
def get_minor_diatonic_triads(key):
    base_note = KEY_MAP[key]
    minor_diatonic_triads = [
        [base_note, base_note + 3, base_note + 7],
        [base_note + 2, base_note + 5, base_note + 8],
        [base_note + 3, base_note + 7, base_note + 10],
        [base_note + 5, base_note + 8, base_note + 12],
        [base_note + 7, base_note + 10, base_note + 14],
        [base_note + 8, base_note + 12, base_note + 15],
        [base_note + 10, base_note + 14, base_note + 17],
        [base_note + 12, base_note + 15, base_note + 19],
    ]

    # adjust based on octave
    octave_adjusted_triads = [[z + octave * 12 for z in y] for y in minor_diatonic_triads for octave in range(8)]
    return octave_adjusted_triads


# major scale
def get_major_scale(key):
    base_note = KEY_MAP[key]
    major_key = [0, 2, 4, 5, 7, 9, 11, 12]
    major_key = [base_note + i for i in major_key]
    full_scale = []
    for octave in range(8):
        full_scale += [z + octave * 12 for z in major_key]

    return full_scale


# natural minor scale
def get_minor_scale(key):
    base_note = KEY_MAP[key]
    minor_key = [0, 2, 3, 5, 7, 8, 10, 12]
    minor_key = [base_note + i for i in minor_key]
    full_scale = []
    for octave in range(8):
        full_scale += [z + octave * 12 for z in minor_key]

    return full_scale


class TheoryLoss(torch.nn.Module):
    def __init__(self, key):
        self.key = key
        super(TheoryLoss, self).__init__()

    def forward(self, x, y):
        major_scale = get_major_scale(self.key)
        minor_scale = get_minor_scale(self.key)

        minor_diatonic_triads = get_minor_diatonic_triads(self.key)
        major_diatonic_triads = get_major_diatonic_triads(self.key)

        loss = 1000

        for i, note in enumerate(y):
            if note > 100:
                loss += 1000

            if i >= 3:
                prev_section = list(y[i - 2 : i])
                mid_section = list(y[i - 2 : i + 1])
                next_section = list(y[i : i + 2])
                previous_count = prev_section.count(note)
                if previous_count > 2:
                    loss += 100

                # check major
                for triad in major_diatonic_triads:
                    if note in triad:
                        overlap = set(triad).intersection(prev_section)
                        if len(overlap) > 1:
                            loss -= 100

                # check minor
                for triad in minor_diatonic_triads:
                    if note in triad:
                        overlap = set(triad).intersection(prev_section)
                        if len(overlap) > 1:
                            loss -= 100

        return loss
