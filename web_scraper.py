from urllib.request import urlopen as uReq
from bs4 import BeautifulSoup as soup
import re
import requests
import itertools

# grab the page
print('Starting to download')
url = 'https://jazzomat.hfm-weimar.de/dbformat/synopsis/'
f = open('metadata.qsv', 'w+')
f.write('file_name?chord_prog?num_bars_prog?num_bars_total?style')
for i in range(1,456):
    client = uReq(url + 'solo' + str(i) + '.html')
    page_html = client.read()
    client.close()

    #format page in bs
    page_soup = soup(page_html, 'html.parser')

    #retrieve midi file
    container = page_soup.find('div',{'id':'midi'})
    midi_file = container.p.a['href']
    file_name = midi_file.split('/')[-1]

    #download the song
    print('Downloading Song: '+midi_file.split('/')[-1])
    response = requests.get(url + midi_file)
    with open('dataset/' + midi_file.split('/')[-1], 'wb+') as fp:
        fp.write(response.content)

    #find style
    container = page_soup.find('div', {'id':'discographic-information'}).find_all('tr')
    style = container[10].find_all('td')[1].text.upper()

    #find the chord progression
    container = page_soup.find('div', {'class','highlight'}).find_all('span')
    chord_raw = ''
    bass_note_flag = 0 
    NC_flag = False 
    for s in container:
        for char in s.text:
            if char == 'N':
                NC_flag = True 
                chord_raw += char
                continue
            if NC_flag:
                if char == 'C':
                    NC_flag = False
                continue
            if char == '/':
                bass_note_flag = 2 
                continue
            if bass_note_flag:
                if char == '|' or char.isupper():
                    bass_note_flag -= 1 
                    if bass_note_flag:
                        continue
                else:
                    continue
            chord_raw += char 

    chord_raw = chord_raw.replace(' ', '')
    chord_raw = [measure for measure in chord_raw.split('||') if ':' not in measure]
    chord_raw = [bar.split('|') for bar in chord_raw]
    chords = list(itertools.chain.from_iterable(chord_raw))
    for i, bar in enumerate(chords):
        sep_chords = re.findall('[A-Z][^A-Z]*', bar)
        chords[i] = '|'.join(sep_chords)

    prog = '||'.join(chords)
    num_bars_prog = len(chords)

    #find the chord progression metadata
    container = page_soup.find('div', {'id':'features'})
    container = container.find('tr', {'class','row-even'}).findAll('td')[1]

    num_bars_total = container.text.split(' ')[0]

    # write to csv
    f.write(file_name + '?' + prog + '?' + str(num_bars_prog) + '?'\
            + str(num_bars_total) + '?' + style + '\n')
    print(file_name)
    print(prog)
    print('num bars progression: ' + str(num_bars_prog))
    print('num bars solos: ' + str(num_bars_total))
    print('style: ' + style)
    print('=================================')
