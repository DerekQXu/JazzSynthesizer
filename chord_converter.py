import pandas as pd
import numpy as np
import re
from musthe import *

def extension(chord, tonic, extra):
    # add extensions
    if 'b5' in extra:
        chord.append(tonic + 6)
    if '9b' in extra:
        chord.append(tonic + 13)
    if '9#' in extra:
        chord.append(tonic + 15)
    if '11#' in extra:
        chord.append(tonic + 18)
    if '13b' in extra:
        chord.append(tonic + 20)
    if '6' in extra:
        chord.append(tonic + 9)
    if '9' in extra:
        chord.append(tonic + 14)
    if '11' in extra:
        chord.append(tonic + 17)
    if '13' in extra:
        chord.append(tonic + 21)
    proc_chord = np.zeros(128)
    proc_chord[np.array(chord)] = 1
    return proc_chord

data = pd.read_csv('metadata.qsv', delimiter='?')
filtr = pd.read_csv('valid_files.csv', delimiter=',')
data = data[data['file_name'].isin(filtr['valid_files'])]
print(data[0:3])
#print(len(data['chord_prog']))
progs = data['chord_prog']
print('number of valid progressions: ' + str(len(progs)))

progs_proc = [None] * len(progs)
print('split by bar and chord')
for i, prog in enumerate(progs):
    bar = prog.split('||')[:-1]
    progs_proc[i] = [chords.split('|') for chords in bar]

max_len = 0
print('translate the chords')
feature_list =  []
for i, prog in enumerate(progs_proc):
    '''
    # ERROR: indx changes!
    print(i)
    print(progs[1])
    print(prog)
    '''
    cur_len = 0
    feature = []
    for j, bar in enumerate(prog):
        cur_bar = []
        note_length = len(bar)/1.5
        for k, chord in enumerate(bar):
            formatted = re.split('(\d+)',chord)
            chord = formatted[0]
            extra = ''.join(formatted[1:])
            
            # find bass chord
            if 'N' in chord:
                cur_chord_proc = np.ones(129)
                feature.append(cur_chord_proc)
                continue
            elif '-j' in chord:
                tonic = Note(chord.replace('-j', '')).midi_note()
                third = tonic + 3
                seventh = tonic + 7
                eleventh = tonic + 11
                cur_chord = [tonic, third, seventh, eleventh]
                cur_chord_proc = extension(cur_chord, tonic, extra)
                feature.append(np.append(cur_chord_proc,note_length))
                continue
            elif 'sus' in chord:
                tonic = Note(chord.replace('sus', '')).midi_note()
                fifth = tonic + 5
                seventh = tonic + 7 
                cur_chord = [tonic, fifth, seventh]
                cur_chord_proc = extension(cur_chord, tonic, extra)
                feature.append(np.append(cur_chord_proc,note_length))
                continue
            elif '+' in chord:
                chord = chord.replace('+j','aug')
                chord = chord.replace('+','aug')
            elif 'o' in chord:
                chord = chord.replace('o','dim')
            elif '-' in chord or 'm' in chord:
                chord = chord.replace('-','m')
            elif 'j' in chord:
                chord = chord.replace('j','M')
            else:
                chord = chord+'M'
            
            if '7' in extra:
                chord += '7'
            _ = Chord(chord)
            tonic = _.notes[0].midi_note()
            cur_chord = [note.midi_note() for note in _.notes]
            cur_chord_proc = extension(cur_chord, tonic, extra)
            # update
            #pad_flag = np.zeros(131)
            #pad_flags = np.matrix([pad_flag]*(max_len - len(input)))
            #np.hstack(input, pad_flags.T)

            feature.append(np.append(cur_chord_proc,note_length))

            cur_len += 1

    feature_list.append(np.array(feature))
    if cur_len > max_len:
        max_len = cur_len

pad_flag = np.zeros(129)
features = np.zeros([len(feature_list), 129, max_len])
for i, feature in enumerate(feature_list):
    pad_flags = np.matrix([pad_flag]*(max_len - len(feature)))
    if max_len != len(feature):
        features[i] = np.hstack((feature.T, pad_flags.T))

print('max length: ' + str(max_len))
print('final shape:')
print(features.shape)

np.save('X.pckl', features, allow_pickle=True)
