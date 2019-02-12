from mido import MidiFile
import numpy as np
import pandas as pd

data = pd.read_csv('metadata.qsv', delimiter = '?')
df = pd.DataFrame()
path = 'dataset/'

solos_proc = []
times_proc = []
times_total_proc = []
print('converting midi to pandas dataframe')
for file_name in data['file_name']:
    try:
        mid = MidiFile(path + file_name)
    except:
        print('ERROR: invalid midi format!')
        print(file_name)
        continue
    if len(mid.tracks) != 1:
        print ('ERROR: there are ' + len(mid.tracks) + ' tracks')

    # create input to NN:
    prev_time = float(0)
    notes = np.zeros([len(mid.tracks[-1][4:-1]), 128]) # there are 128 notes
    times = np.zeros([len(mid.tracks[-1][4:-1])])
    solo_proc = []
    time_proc = []
    for i, mess in enumerate(mid.tracks[-1][4:-1]):
        if not mess.is_meta:
            notes[i, mess.note] = mess.velocity
            times[i] = prev_time
            prev_time += mess.time
            solo_proc.append(notes)
            time_proc.append(times)
    solos_proc.append(solo_proc)
    times_proc.append(time_proc)
    times_total_proc.append(prev_time)

note_values = pd.DataFrame({'note_values': solos_proc}) 
note_duration = pd.DataFrame({'note_duration': times_proc}) 
song_duration = pd.DataFrame({'song_duration': times_total_proc})

final_df = pd.concat([data['file_name'],note_values,note_duration,song_duration], axis = 1)
print(final_df.shape)
final_df.to_pickle('solos.pickle')
