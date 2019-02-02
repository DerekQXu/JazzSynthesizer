from urllib.request import urlopen as uReq
from bs4 import BeautifulSoup as soup
import requests

# grab the page
print('Starting to download')
url = 'https://jazzomat.hfm-weimar.de/dbformat/synopsis/'
for i in range(1,456):
    client = uReq(url + 'solo' + str(i) + '.html')
    page_html = client.read()
    client.close()

    #format page in bs
    page_soup = soup(page_html, 'html.parser')
    container = page_soup.find('div',{'id':'midi'})
    midi_file = container.p.a['href']

    #download the song
    print('Downloading Song: '+midi_file.split('/')[-1])
    response = requests.get(url + midi_file)
    with open('dataset/' + midi_file.split('/')[-1], 'wb+') as fp:
        fp.write(response.content)
