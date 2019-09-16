#DIATONIC TRIADS

note = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24]


def major_diatonic_triads(key):
    major_diatonic = []
    #I
    major_diatonic.append([note[key], note[key + 4], note[key + 7]])
    #ii
    major_diatonic.append([note[key + 2], (note[key + 2] + 3), (note[key + 2] + 7)])
    #iii
    major_diatonic.append([note[key + 4], (note[key + 4] + 3), (note[key + 4] + 7)])
    #IV
    major_diatonic.append([note[key + 5], (note[key + 5] + 4), (note[key + 5] + 7)])
    #V
    major_diatonic.append([note[key + 7], (note[key + 7] + 4), (note[key + 7] + 7)])
    #vi
    major_diatonic.append([note[key + 9], (note[key + 9] + 3), (note[key + 9] + 7)])
    #vii
    major_diatonic.append([note[key + 11], (note[key + 11] + 3), (note[key + 11] + 6)])
    #I2
    major_diatonic.append([note[key + 12], (note[key + 12] + 3), (note[key + 12] + 7)])

    return major_diatonic

C_Major_Diatonic = major_diatonic_triads(0)
Cs_Major_Diatonic = major_diatonic_triads(1)
D_Major_Diatonic = major_diatonic_triads(2)
Ds_Major_Diatonic = major_diatonic_triads(3)
print(C_Major_Diatonic)

#prints [[0,4,7],[2,5,9], [4,7,11], [5,9,12], [7,11,14], [9,12,16], [11,14,17], [12,15,19]]
#          I       ii       iii       IV          V         vi         vii           I2



def minor_diatonic_triads(key):
    minor_diatonic = []
    #I
    minor_diatonic.append([note[key], note[key + 4], note[key + 7]])
    #ii
    minor_diatonic.append([note[key + 2], (note[key + 2] + 3), (note[key + 2] + 7)])
    #iii
    minor_diatonic.append([note[key + 3], (note[key + 3] + 3), (note[key + 3] + 6)])
    #IV
    minor_diatonic.append([note[key + 5], (note[key + 5] + 4), (note[key + 5] + 7)])
    #V
    minor_diatonic.append([note[key + 7], (note[key + 7] + 3), (note[key + 7] + 7)])
    #vi
    minor_diatonic.append([note[key + 8], (note[key + 8] + 3), (note[key + 8] + 7)])
    #vii
    minor_diatonic.append([note[key + 10], (note[key + 10] + 4), (note[key + 10] + 7)])
    #I2
    minor_diatonic.append([note[key + 12], (note[key + 12] + 3), (note[key + 12] + 7)])

    return minor_diatonic

C_Minor_Diatonic = minor_diatonic_triads(0)
Cs_Minor_Diatonic = minor_diatonic_triads(1)

print(C_Minor_Diatonic)


#prints[[0,4,7], [2,5,9], [3,6,9], [5,9,12], [7,10,14], [8,11,15], [10,14,17], [12,15,19]]
#          I        ii       iii      VI           V         vi        vii         I2
