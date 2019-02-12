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
progs = data['chord_prog'].copy()

print('split by bar and chord')
for i, prog in enumerate(progs):
    bar = prog.split('||')[:-1]
    progs[i] = [chords.split('|') for chords in bar]

print('translate the chords')
for i, prog in enumerate(progs):
    cur_prog = []
    for j, bar in enumerate(prog):
        cur_bar = []
        for k, chord in enumerate(bar):
            formatted = re.split('(\d+)',chord)
            chord = formatted[0]
            extra = ''.join(formatted[1:])
            
            # find bass chord
            if 'N' in chord:
                cur_chord_proc = np.ones(128)
                progs[i][j][k] = cur_chord_proc
                continue
            elif '-j' in chord:
                tonic = Note(chord.replace('-j', '')).midi_note()
                third = tonic + 3
                seventh = tonic + 7
                eleventh = tonic + 11
                cur_chord = [tonic, third, seventh, eleventh]
                cur_chord_proc = extension(cur_chord, tonic, extra)
                progs[i][j][k] = cur_chord_proc 
                continue
            elif 'sus' in chord:
                tonic = Note(chord.replace('sus', '')).midi_note()
                fifth = tonic + 5
                seventh = tonic + 7 
                cur_chord = [tonic, fifth, seventh]
                cur_chord_proc = extension(cur_chord, tonic, extra)
                progs[i][j][k] = cur_chord_proc 
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
            progs[i][j][k] = cur_chord_proc 
            
final_df = pd.concat([data['file_name'],progs,data['num_bars_total'],data['num_bars_prog']], axis = 1)
print(final_df.shape)
final_df.to_pickle('chords.pickle')
