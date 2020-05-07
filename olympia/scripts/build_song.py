import logging
from music21 import roman, stream, note, chord, instrument, duration
import json
import numpy as np
import copy
from olympia import files, utils
from olympia.data.song import Song
from olympia.train import ModelSettings
from olympia.models import lstm
from olympia import ROOT_DIR

logger = logging.getLogger("olympia")
logging.basicConfig(level=logging.DEBUG, format="%(message)s")


INSTRUMENT_PART_MAP = {
    "piano": instrument.Piano(),
    "bass": instrument.Bass(),
}


START_PITCH_MAP = {"piano": {"C": [60, 67],}, "bass": {"C": [43]}}


def map_values(values, mapping):
    mapped_values = []
    for val in values:
        result = list(mapping.keys())[list(mapping.values()).index(val)]
        mapped_values.append(result)
    return mapped_values


class Model:
    def __init__(self, model_hash, sequence=False):
        self.model = files.get_model(model_hash)
        self.settings = ModelSettings(**utils.load_model_settings(model_hash))
        self.output = None
        self.mapping = None

        self.sequence_length = self.settings.sequence_length
        self.epochs = self.settings.epochs
        self.learning_rate = self.settings.learning_rate
        self.instrument = self.settings.instrument
        self.hidden_layer = self.settings.hidden_layer
        self.create_date = self.settings.create_date
        self.sequence_length = self.settings.sequence_length
        self.n_clusters = self.settings.n_clusters

        if not sequence:
            self.mapping = files.get_mapping(model_hash)

    def generate_random_output(self, n_samples):
        output = lstm.generate_random_output(self, n_samples=n_samples)

        if self.mapping:
            output = map_values(output, self.mapping)

        self.output = output
        return output


class InstrumentModel:
    def __init__(self, instrument, duration_hash, harmony_hash):
        self.instrument = instrument
        # load models
        self.duration_model = Model(duration_hash)
        self.harmony_model = Model(harmony_hash)
        self.duration_output = None
        self.harmony_output = None

    def generate_outputs(self, sequence, key, n_notes):
        raw_durations = self.duration_model.generate_random_output(n_notes)
        raw_harmony = self.harmony_model.generate_random_output(n_notes)
        raw_harmony = [float(note) for note in raw_harmony]

        self.duration_output, self.harmony_output = generate(raw_durations, raw_harmony, sequence)


# CLASS: SongBuilder
# DESCRIPTION: Class for loading models and building songs
class SongBuilder:
    def __init__(self, instruments, sequence_hash, harmony_maps, duration_maps, key, n_sections, n_mes):

        self.duration_maps = duration_maps
        self.harmony_maps = harmony_maps

        # load sequence model and generate governing sequence
        self.sequence = None
        self.sequence_model = Model(sequence_hash, sequence=True)
        self.n_sections = n_sections

        self.midi_stream = stream.Stream()

        self.key = key
        self.n_notes = n_sections * n_mes * 10  # produce extra for more material
        self.instruments = instruments

        # for populating loaded models
        self.instrument_models = []
        self.load_models()

    # METHOD: load_models
    # DESCRIPTION: loads models for all instruments
    def load_models(self):

        # select models based on instrument
        for instrument in self.instruments:
            harmony_hash = self.harmony_maps[instrument]
            duration_hash = self.duration_maps[instrument]
            self.instrument_models.append(InstrumentModel(instrument, duration_hash, harmony_hash))

    def build_sequence(self):
        # build sequence output
        self.sequence = self.sequence_model.generate_random_output(self.n_sections)

    def build_instrument_parts(self):

        instrument_part = stream.Part()
        for instrument_model in self.instrument_models:
            instrument_model.generate_outputs(
                self.sequence, self.key, self.n_notes,
            )

            instrument_part = stream.Part()
            instrument_part.append(INSTRUMENT_PART_MAP[instrument_model.instrument])

            for i, pitch_number in enumerate(instrument_model.harmony_output):
                new_note = note.Note(quarterLength=instrument_model.duration_output[i])
                new_note.offset = instrument_part.highestTime
                new_note.pitch.ps = pitch_number
                instrument_part.append(new_note)

            self.midi_stream.append(instrument_part)

    def write_midi(self, song_name):
        save_file = ROOT_DIR + "/olympia/files/songs/" + song_name
        breakpoint()
        self.midi_stream.write("midi", fp=save_file)

    def build_song(self):
        self.build_sequence()
        self.build_instrument_parts()
        self.write_midi("test.mid")


def generate(durations, harmonies, sequence, n_meas_per_section=2, meas_len=4):
    n_sections = len(sequence)

    quarter_note_durations = [duration.Duration(type=dur).quarterLength for dur in durations]

    i = 1
    sections = []
    for i in range(len(durations)):
        logger.debug("Processing %s of %s", i, len(durations))

        # allowed durations
        allowed_durations = quarter_note_durations[i:]

        section_durations = []

        # populate until full measures
        j = 1
        while sum(allowed_durations[:j]) < n_meas_per_section * meas_len and len(allowed_durations[: j + 1]) > len(
            allowed_durations[:j]
        ):
            section_durations = allowed_durations[: j - 1]
            j += 1

        # if full section found
        if section_durations:

            # adjust to fill duration section to full n measures
            if sum(section_durations) < n_meas_per_section * meas_len:
                section_durations[-1] = n_meas_per_section * meas_len - sum(section_durations[:-1])

            # now populate harmonies
            section_harmony = harmonies[i : i + len(section_durations)]

            sections.append({"durations": section_durations, "harmony": section_harmony})

    # rank based off of the unique values in section and harmony
    # keep only the n most diverse (where n is the set of unique sections)
    diversity_ranked_sections = sorted(sections, key=lambda k: len(set(k["durations"])) + len(set(k["harmony"])))[
        -len(set(sequence)) :
    ]
    sequence_map = {}

    # using generated sequences, sort based off of frequency
    sorted_sequence_freq = sorted(set(sequence), key=sequence.count)

    logger.debug("Len sorted freq: %s", len(sorted_sequence_freq))
    logger.debug("len diversity ranked: %s", len(diversity_ranked_sections))

    # map to highest diversity sections
    for i, item in enumerate(sorted_sequence_freq):
        print(i)
        sequence_map[item] = diversity_ranked_sections[i]

    new_duration = []
    new_harmony = []

    # build new midi
    for i in range(n_sections):
        seq_assign = sequence_map[sequence[i]]
        new_duration += seq_assign["durations"]
        new_harmony += seq_assign["harmony"]

    return new_duration, new_harmony


if __name__ == "__main__":
    instruments = ["piano", "bass"]
    sequence_hash = "6f1780afe238fdfa1cb812c632e1cf55"
    harmony_maps = {"piano": "57aef87a0f63963a2a3cb9444903f838", "bass": "be192b20d444a306cd75d8e51fb25cbe"}
    duration_maps = {"piano": "204e5d35829fad05e619bd57859bcf90", "bass": "204e5d35829fad05e619bd57859bcf90"}
    key = "C"
    n_sections = 15
    n_mes = 4

    builder = SongBuilder(instruments, sequence_hash, harmony_maps, duration_maps, key, n_sections, n_mes)
    builder.build_song()

