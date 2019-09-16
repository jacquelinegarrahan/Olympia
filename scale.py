
#start with the note values represented as numbers
note = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24]
#       C  Cs D  Ds E  F  Fs G  Gs A  As  B   C   Cs2  D2 Ds2 E2  F2  Fs2 G2  Gs2 A2  As2 B2  C3

def major_scale(key):
    major_key = []
    major_key.append(note[key])
    major_key.append(note[key + 2])
    major_key.append(note[key + 4])
    major_key.append(note[key + 5])
    major_key.append(note[key + 7])
    major_key.append(note[key + 9])
    major_key.append(note[key + 11])
    major_key.append(note[key + 12])
    return major_key
#using the major scale intervals to create new list with only notes within that scale
c_major = major_scale(0)
print(c_major)
#prints [0, 2, 4, 5, 7, 9, 11, 12]
#aka:   [C, D, E, F, G, A, B, C] which is the CMajor scale

#heres the same thing but using the minor scale intervals
def minor_scale(key):
    minor_key = []
    minor_key.append(note[key])
    minor_key.append(note[key + 2])
    minor_key.append(note[key + 3])
    minor_key.append(note[key + 5])
    minor_key.append(note[key + 7])
    minor_key.append(note[key + 8])
    minor_key.append(note[key + 10])
    minor_key.append(note[key + 12])
    return minor_key
c_minor = minor_scale(0)
print(c_minor)
#prints [0, 2, 3, 5, 7, 8, 10, 12]
#aka:   [C, D, D#, F, G, G#, A#, C] which is the CMinor scale





#OCTAVES

#could even use math to reach the whole span of octaves you have available

note = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24]
#       C  Cs D  Ds E  F  Fs G  Gs A  As  B   C   Cs2  D2 Ds2 E2  F2  Fs2 G2  Gs2 A2  As2 B2  C3

def major_scale(key):
    major_key = []
    major_key.append(note[key])
    major_key.append(note[key + 2])
    major_key.append(note[key + 4])
    major_key.append(note[key + 5])
    major_key.append(note[key + 7])
    major_key.append(note[key + 9])
    major_key.append(note[key + 11])
    major_key.append(note[key + 12])
    major_key_octave2 = [knote + 12 for knote in major_key]
    major_key_octave3 = [knote + 12 for knote in major_key_octave2]
    all_octaves = major_key + major_key_octave2 + major_key_octave3
    return all_octaves

c_major_scale_3octaves = major_scale(0)
print(c_major_scale_3octaves)

note = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24]
#       C  Cs D  Ds E  F  Fs G  Gs A  As  B   C   Cs2  D2 Ds2 E2  F2  Fs2 G2  Gs2 A2  As2 B2  C3


def minor_scale(key):
    minor_key = []
    minor_key.append(note[key])
    minor_key.append(note[key + 2])
    minor_key.append(note[key + 3])
    minor_key.append(note[key + 5])
    minor_key.append(note[key + 7])
    minor_key.append(note[key + 8])
    minor_key.append(note[key + 10])
    minor_key.append(note[key + 12])
    minor_key_octave2 = [knote + 12 for knote in minor_key]
    minor_key_octave3 = [knote + 12 for knote in minor_key_octave2]
    all_octaves = minor_key + minor_key_octave2 + minor_key_octave3
    return all_octaves

c_minor_scale_3octaves = minor_scale(0)
print(c_minor_scale_3octaves)

# prints [0, 2, 3, 5, 7, 8, 10, 12, 12, 14, 15, 17, 19, 20, 22, 24, 24, 26, 27, 29, 31, 32, 34, 36]
# this is just the C Minor scale but now spanning 3 octaves



#random melody generator

import random

def melody(scale, measures):
    new_melody = []
    new_melody_amount = len(new_melody)
    while new_melody_amount < measures:
        new_melody.append(random.choice(scale))
    return new_melody

c_major_melody = melody(c_major_scale_3octaves, 6)
