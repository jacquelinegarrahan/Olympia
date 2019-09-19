#added all octaves for triads,
#still need to find a way
#to stop it from going over 100



note = range(100)

#major diatonic triads
def major_diatonic_triads(key):
    major_diatonic = []
    major_diatonic.append([note[key], note[key + 4], note[key + 7]])
    major_diatonic.append([note[key + 2], (note[key + 2] + 3), (note[key + 2] + 7)])
    major_diatonic.append([note[key + 4], (note[key + 4] + 3), (note[key + 4] + 7)])
    major_diatonic.append([note[key + 5], (note[key + 5] + 4), (note[key + 5] + 7)])
    major_diatonic.append([note[key + 7], (note[key + 7] + 4), (note[key + 7] + 7)])
    major_diatonic.append([note[key + 9], (note[key + 9] + 3), (note[key + 9] + 7)])
    major_diatonic.append([note[key + 11], (note[key + 11] + 3), (note[key + 11] + 6)])
    major_diatonic.append([note[key + 12], (note[key + 12] + 4), (note[key + 12] + 7)])
    octave_2 = [[z + 12 for z in y] for y in major_diatonic]
    octave_3 = [[z + 24 for z in y] for y in major_diatonic]
    octave_4 = [[z + 36 for z in y] for y in major_diatonic]
    octave_4 = [[z + 48 for z in y] for y in major_diatonic]
    octave_5 = [[z + 60 for z in y] for y in major_diatonic]
    octave_6 = [[z + 72 for z in y] for y in major_diatonic]
    octave_7 = [[z + 84 for z in y] for y in major_diatonic]
    octaves_sum = major_diatonic + octave_2 + octave_3 + octave_4 + octave_5 + octave_6 + octave_7
    from itertools import groupby
    all_octaves = [i[0] for i in groupby(octaves_sum)]
    return all_octaves

c_maj_triads = major_diatonic_triads(0)
c_sharp_maj_triads = major_diatonic_triads(1)
d_flat_maj_triads = major_diatonic_triads(1)
d_maj_triads = major_diatonic_triads(2)
d_sharp_maj_triads = major_diatonic_triads(3)
e_flat_maj_triads = major_diatonic_triads(3)
e_maj_triads = major_diatonic_triads(4)
f_maj_triads = major_diatonic_triads(5)
f_sharp_maj_triads = major_diatonic_triads(6)
g_flat_maj_triads = major_diatonic_triads(6)
g_maj_triads = major_diatonic_triads(7)
g_sharp_maj_triads = major_diatonic_triads(8)
a_flat_maj_triads = major_diatonic_triads(8)
a_maj_triads = major_diatonic_triads(9)
a_sharp_maj_triads = major_diatonic_triads(10)
b_flat_maj_triads = major_diatonic_triads(10)
b_maj_triads = major_diatonic_triads(11)


#natural minor diatonic triads
def minor_diatonic_triads(key):
    minor_diatonic = []
    minor_diatonic.append([note[key], note[key + 3], note[key + 7]])
    minor_diatonic.append([note[key + 2], (note[key + 2] + 3), (note[key + 2] + 6)])
    minor_diatonic.append([note[key + 3], (note[key + 3] + 4), (note[key + 3] + 7)])
    minor_diatonic.append([note[key + 5], (note[key + 5] + 3), (note[key + 5] + 7)])
    minor_diatonic.append([note[key + 7], (note[key + 7] + 3), (note[key + 7] + 7)])
    minor_diatonic.append([note[key + 8], (note[key + 8] + 4), (note[key + 8] + 7)])
    minor_diatonic.append([note[key + 10], (note[key + 10] + 4), (note[key + 10] + 7)])
    minor_diatonic.append([note[key + 12], (note[key + 12] + 3), (note[key + 12] + 7)])
    octave_2 = [[z + 12 for z in y] for y in minor_diatonic]
    octave_3 = [[z + 24 for z in y] for y in minor_diatonic]
    octave_4 = [[z + 36 for z in y] for y in minor_diatonic]
    octave_4 = [[z + 48 for z in y] for y in minor_diatonic]
    octave_5 = [[z + 60 for z in y] for y in minor_diatonic]
    octave_6 = [[z + 72 for z in y] for y in minor_diatonic]
    octave_7 = [[z + 84 for z in y] for y in minor_diatonic]
    octaves_sum = minor_diatonic + octave_2 + octave_3 + octave_4 + octave_5 + octave_6 + octave_7
    from itertools import groupby
    all_octaves = [i[0] for i in groupby(octaves_sum)]
    return all_octaves

c_min_triads = minor_diatonic_triads(0)
c_sharp_min_triads = minor_diatonic_triads(1)
d_flat_min_triads = minor_diatonic_triads(1)
d_min_triads = minor_diatonic_triads(2)
d_sharp_min_triads = minor_diatonic_triads(3)
e_flat_min_triads = minor_diatonic_triads(3)
e_min_triads = minor_diatonic_triads(4)
f_min_triads = minor_diatonic_triads(5)
f_sharp_min_triads = minor_diatonic_triads(6)
g_flat_min_triads = minor_diatonic_triads(6)
g_min_triads = minor_diatonic_triads(7)
g_sharp_min_triads = minor_diatonic_triads(8)
a_flat_min_triads = minor_diatonic_triads(8)
a_min_triads = minor_diatonic_triads(9)
a_sharp_min_triads = minor_diatonic_triads(10)
b_flat_min_triads = minor_diatonic_triads(10)
b_min_triads = minor_diatonic_triads(11)
