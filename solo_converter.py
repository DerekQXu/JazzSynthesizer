from mido import MidiFile
import numpy as np
import pandas as pd

f = open('valid_files.csv', 'w+')
f.write('valid_files\n')
data = pd.read_csv('metadata.qsv', delimiter = '?')
df = pd.DataFrame()
path = 'dataset/'

#len_threshold = float('inf')
len_threshold = 1000
end_flag = np.zeros(130) # 128 notes + <EOS> + <PAD>
pad_flag = np.zeros(131) # 128 notes + <EOS> + <PAD> + <time>
end_flag[-3] = 100
pad_flag[-2] = 100 
max_len = 0
print('converting midi to numpy array')

# find the max length
for file_name in data['file_name']:
    mid = MidiFile(path + file_name)
    cur_len = 0

    for i, mess in enumerate(mid.tracks[-1][4:-1]):
        if not mess.is_meta:
            cur_len += 1

    cur_len += 1
    if cur_len > max_len and cur_len < len_threshold:
        max_len = cur_len 

features = np.zeros([len(data['file_name']), 131, max_len])

# create our input data
indx = 0
valid_file_names = []
for file_name in data['file_name']:
    print('processing ' + file_name)
    try:
        mid = MidiFile(path + file_name)
    except:
        print('ERROR: invalid midi format!')
        print(file_name)
        continue
    if len(mid.tracks) != 1:
        print ('ERROR: there are ' + len(mid.tracks) + ' tracks')

    notes = np.zeros([130]) # there are 128 notes + end flag + pad flag

    solo_proc = []
    time_proc = []

    for mess in mid.tracks[-1][4:-1]:
        if not mess.is_meta:
            notes[mess.note] = 100 #mess.velocity
            solo_proc.append(notes)
            time_proc.append(mess.time)

    solo_proc.append(end_flag)
    time_proc.append(0)

    pad_flags = np.matrix([pad_flag]*(max_len - len(solo_proc)))
    if max_len > len(solo_proc):
        feature = np.hstack(\
            (np.vstack(\
                (np.matrix(solo_proc).T, np.array(time_proc))\
            ), pad_flags.T)\
        )
    else:
        feature = np.vstack((np.matrix(solo_proc).T, np.array(time_proc)))

    if len(solo_proc) < len_threshold:
        f.write(file_name + '\n')
        features[indx] = feature
        indx += 1

features = features[0:indx]
print('feature shape:')
print(features.shape)

print('saving features')
np.save('y.pckl', features, allow_pickle=True)
