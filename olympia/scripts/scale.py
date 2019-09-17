note = range(100)

#added variables for all scales based
#on starting note value,
#got rid of duplicating numbers
#and stopped it from going over 100


#major scale
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
    octave2 = [knote + 12 for knote in major_key]
    octave3 = [knote + 12 for knote in octave2]
    octave4 = [knote + 12 for knote in octave3]
    octave5 = [knote + 12 for knote in octave4]
    octave6 = [knote + 12 for knote in octave5]
    octave7 = [knote + 12 for knote in octave6]
    octave8 = [knote + 12 for knote in octave7]
    octaves_sum = major_key + octave2 + octave3 + octave4 + octave5 + octave6 + octave7 + octave8
    from itertools import groupby
    all_octaves = [i[0] for i in groupby(octaves_sum)]
    full_scale =[]
    for noet in all_octaves:
        if noet < 101:
            full_scale.append(noet)
    return full_scale
    return all_octaves


c_major = major_scale(0)
c_sharp_major = major_scale(1)
d_flat_major = major_scale(1)
d_major = major_scale(2)
d_sharp_major = major_scale(3)
e_flat_major = major_scale(3)
e_major = major_scale(4)
f_major = major_scale(5)
f_sharp_major = major_scale(6)
g_flat_major = major_scale(6)
g_major = major_scale(7)
g_sharp_major = major_scale(8)
a_flat_major = major_scale(8)
a_major = major_scale(9)
a_sharp_major = major_scale(10)
b_flat_major = major_scale(10)
b_major = major_scale(11)



#natural minor scale
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
    octave2 = [knote + 12 for knote in minor_key]
    octave3 = [knote + 12 for knote in octave2]
    octave4 = [knote + 12 for knote in octave3]
    octave5 = [knote + 12 for knote in octave4]
    octave6 = [knote + 12 for knote in octave5]
    octave7 = [knote + 12 for knote in octave6]
    octave8 = [knote + 12 for knote in octave7]
    octaves_sum = minor_key + octave2 + octave3 + octave4 + octave5 + octave6 + octave7 + octave8
    from itertools import groupby
    all_octaves = [i[0] for i in groupby(octaves_sum)]
    full_scale =[]
    for noet in all_octaves:
        if noet < 101:
            full_scale.append(noet)
    return full_scale

c_minor = minor_scale(0)
c_sharp_minor = minor_scale(1)
d_flat_minor = minor_scale(1)
d_minor = minor_scale(2)
d_sharp_minor = minor_scale(3)
e_flat_minor = minor_scale(3)
e_minor = minor_scale(4)
f_minor= minor_scale(5)
f_sharp_minor = minor_scale(6)
g_flat_minor = minor_scale(6)
g_minor = minor_scale(7)
g_sharp_minor = minor_scale(8)
a_flat_minor = minor_scale(8)
a_minor = minor_scale(9)
a_sharp_minor = minor_scale(10)
b_flat_minor = minor_scale(10)
b_minor = minor_scale(11)
