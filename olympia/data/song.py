from music21 import instrument, midi, chord, pitch, roman, stream
from music21.stream import Part as StreamPart
from typing import List
import numpy as np
import boto3
import logging
from sklearn.cluster import KMeans
from sklearn.preprocessing import normalize

from olympia import files, db
from olympia import ROOT_DIR

logger = logging.getLogger("olympia")
logging.basicConfig(level=logging.DEBUG, format="%(message)s")


class Part:
    def __init__(self, part_obj: StreamPart):

        self.instrument = part_obj.partName
        self.notes = part_obj.notes
        # self.notes_and_rests = part_obj.notesAndRests
        self.pitch_differences = []
        self.harmony = None
        self.roman_numerals = None
        self.pitch_vector = None
        self.duration_progression = None
        self.get_pitch_differences()
        self.chord_progression = part_obj.chordify()
        self.get_harmonic_reduction()
        self.convert_harmonic_to_roman_numerals()
        self.get_duration_progression()

    def get_pitch_differences(self):

        pitch_vector = []
        for note in self.notes:
            if note.isChord:
                pitch_vector.append(note[-1].pitch.ps)

            else:
                pitch_vector.append(note.pitch.ps)

        self.pitches = pitch_vector
        self.pitch_differences = np.diff(pitch_vector)

    def get_harmonic_reduction(self):
        reduction = []

        temp_midi = stream.Score()
        temp_midi.insert(0, self.chord_progression)
        max_notes_per_chord = 4

        for measure in temp_midi.measures(0, None):  # None = get all measures.
            if type(measure) != stream.Measure:
                continue

            # count all notes length in each measure,
            count_dict = note_count(measure)
            sorted_items = sorted(count_dict.items(), key=lambda x: x[1])
            sorted_notes = [item[0] for item in sorted_items[-max_notes_per_chord:]]
            measure_chord = chord.Chord(sorted_notes)

            reduction.append(measure_chord)

        self.harmony = reduction

        return reduction

    def convert_harmonic_to_roman_numerals(self):
        ret = []
        for c in self.harmony:
            if c == "-":
                ret.append("-")
            else:
                roman_numeral = roman.romanNumeralFromChord(c, self.expected_key)
                ret.append(simplify_roman_name(roman_numeral))
        self.roman_numerals = ret
        return ret

    def get_duration_progression(self, prune_complex: bool = True) -> List[str]:
        durations = []

        for nt in self.notes:
            if nt.duration.type != "complex":
                durations.append(nt.duration.type)

        self.duration_progression = durations

        return durations


class Song:
    def __init__(self, raw_path: str, title: str = None, artist: str = None):
        self.title = title
        self.artist = artist
        self.raw_path = raw_path
        self.expected_key = None
        self.time_signature = None
        # self.load_midi()
        self.parts = []
        self.instruments = []
        self.load_midi()

    def load_midi(self, remove_drums: bool = True) -> None:
        mf = midi.MidiFile()
        mf.open(self.raw_path)
        mf.read()
        mf.close()
        # 	if (remove_drums):
        # 		for i in range(len(mf.tracks)):
        # 			mf.tracks[i].events = [ev for ev in mf.tracks[i].events if ev.channel != 10]

        self.midi = midi.translate.midiFileToStream(mf)
        self.get_parts()
        self.get_expected_key()
        self.get_time_signatures()

    def get_parts(self) -> None:
        part_stream = self.midi.parts.stream()
        for p in part_stream:
            part_obj = Part(p)
            self.parts.append(part_obj)
            if part_obj.instrument:
                self.instruments.append(part_obj.instrument)

    def get_stream(self):
        return self.midi.parts.stream()

    def get_part_by_instrument(self, instrument: str) -> Part:
        for p in self.parts:
            if p.instrument and instrument in p.instrument.lower():
                return p

    def get_expected_key(self):
        self.expected_key = self.midi.analyze("key")
        return self.expected_key

    def get_time_signatures(self):
        time_signature = self.midi.getTimeSignatures()[0]
        self.time_signature = "{}/{}".format(time_signature.beatCount, time_signature.denominator)
        return self.time_signature

    def get_cluster_sequence(self, n_mes: int = 1, n_clusters: int = 20):
        representations = []
        measures = self.midi.makeMeasures()
        measures = measures.getElementsByClass("Measure")

        measureDict = {}

        for i in range(int(len(measures) / n_mes)):
            for part in self.parts:
                for nt in part.notes:
                    if nt.offset >= 4 * i * n_mes and nt.offset < 4 * n_mes * (1 + i):
                        if i not in measureDict:
                            measureDict[i] = [nt]
                        else:
                            measureDict[i].append(nt)

        # iterate over measure snippets to create structure
        for i in range(int(len(measures) / n_mes)):
            if i in measureDict:
                measure_offset_rep = []
                measure_note_rep = []

                for mnote in measureDict[i]:
                    if mnote.isChord:
                        for cnote in mnote:
                            measure_offset_rep.append(cnote.offset - 4 * i * n_mes)
                            measure_note_rep.append(cnote.pitch.ps)
                    else:
                        measure_offset_rep.append(mnote.offset - 4 * i * n_mes)
                        measure_note_rep.append(mnote.pitch.ps)

                if len(measure_note_rep) > 0 and len(measure_note_rep) > 0:
                    representations.append([np.mean(measure_offset_rep), np.mean(measure_note_rep)])

        cluster_labels = get_cluster_labels(np.array(representations), n_clusters=n_clusters)

        breakpoint()

        return cluster_labels


def note_count(measure):
    count_dict = {}
    base_note = None
    for m_chord in measure.recurse().getElementsByClass("Chord"):
        # All notes have the same length of its chord parent.
        note_length = m_chord.quarterLength
        for note in m_chord.pitches:
            # If note is "C5", note.name is "C". We use "C5"
            # style to be able to detect more precise inversions.
            note_name = str(note)
            if base_note is None or base_note.ps > note.ps:
                base_note = note

            if note_name in count_dict:
                count_dict[note_name] += note_length
            else:
                count_dict[note_name] = note_length

    return count_dict


def simplify_roman_name(roman_numeral):
    # Attempt to simplify names
    ret = roman_numeral.romanNumeral
    inversion_name = None
    inversion = roman_numeral.inversion()

    # Checking valid inversions.
    if (roman_numeral.isTriad() and inversion < 3) or (
        inversion < 4 and (roman_numeral.seventh is not None or roman_numeral.isSeventh())
    ):
        inversion_name = roman_numeral.inversionName()

    if inversion_name is not None:
        ret = ret + str(inversion_name)

    elif roman_numeral.isDominantSeventh():
        ret = ret + "M7"
    elif roman_numeral.isDiminishedSeventh():
        ret = ret + "o7"
    return ret


def get_cluster_labels(matrix: np.array, n_clusters: int = 20) -> List[int]:
    if matrix.shape[0] > n_clusters:
        normed_matrix = normalize(matrix, axis=1, norm="l1")
        kclusterer = KMeans(n_clusters=n_clusters).fit(normed_matrix)

        labels = kclusterer.labels_
        return labels
    else:
        return []


def get_songs(instrument, time_signature: str = None, key: str = None, limit: int = None) -> List[Song]:
    songs = []

    query = """
    SELECT midi_id FROM midis
    WHERE instruments LIKE :instrument
    """
    params = {"instrument": f"%{instrument}%"}

    if time_signature:
        query += " AND time_signature = :time_signature"
        params["time_signature"] = time_signature

    if key:
        query += " AND key = :key"
        params["key"] = key

    results = db.execute_query(query, params).fetchall()

    songs = []
    if limit:
        results = results[:limit]

    for result in results:
        try:
            midi_id = result[0]
            file_name = f"midis/raw_midi_{midi_id}.mid"
            save_path = f"{ROOT_DIR}/olympia/files/midis/raw_midi_{midi_id}.mid"
            files.download_file(file_name, save_path)
            song_obj = Song(save_path)
            songs.append(song_obj)
        except:
            logger.debug("Error on %s", midi_id)

    return songs
