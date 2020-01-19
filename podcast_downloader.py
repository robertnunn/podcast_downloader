import os
import sys
import bs4
import requests
import re
from selenium import webdriver
from urllib.parse import unquote
from pprint import pprint as pp

def setup(method):
    def wrapper(*args, **kw):
        result = ''

        return result
    return wrapper


def download_podcast(podcast_url, target_folder):
    sites = {   'stitcher': stitcher_download,
                'soundcloud': soundcloud_download,
                'itunes': itunes_download,    
            }  # only currently supporting stitcher
    try:
        os.mkdir(target_folder)
    except FileExistsError as e:
        print('Directory already exists, moving on.')

    for i in sites.keys():
        if i in podcast_url:
            sites[i](podcast_url, target_folder)


def save_file(folder, filename, source_url):
    disallowed = ['/', '\\', '"', '*', '?', '<', '>', '|']
    replacement = [(':', '-')]
    for i in disallowed:
        filename = filename.replace(i, '')
    for i in replacement:
        filename = filename.replace(i[0], i[1])
    
    if os.path.isfile(full_path := folder+filename):
        print(full_path, ' already exists')
    else:
        try:
            audio = requests.get(source_url)
            audio.raise_for_status()
            with open(full_path, 'wb') as ep_audio:
                for chunk in audio.iter_content(100000):
                    ep_audio.write(chunk)
        except requests.HTTPError as e:
            print(f'error, ep_url ({ep_url}) not found: ({e})')


def make_podcast_folder(target_folder, show_name):
    try:
        os.mkdir(f'{target_folder}/{show_name}')
    except FileExistsError as e:
        print(f'({target_folder}/{show_name}) show directory already exists')


def stitcher_download(podcast, target_folder):
    fb = webdriver.Firefox()
    fb.get(podcast)
    xpath_filter = podcast.replace('https://www.stitcher.com', '')
    show_name = xpath_filter[xpath_filter.rfind('/')+1:]
    ep_url_pattern = re.compile('episodeURL: "(.*?)",\n')
    ep_title_pattern = re.compile('<div id="embedPopup">.*?<h2>(.*?)</h2>', flags=re.DOTALL)

    make_podcast_folder(target_folder, show_name)
    end = False
    while end == False:
        try:
            elem = fb.find_element_by_link_text('Load More Episodes')
            elem.click()
        except:
            print("Reached the end")
            end = True
    episode_elems = fb.find_elements_by_xpath(f'//a[contains(@href, "{xpath_filter}")]')
    episode_links = list()
    for i in episode_elems:
        episode_links.append(i.get_attribute('href'))
    fb.close()
    # pp(episode_links)
    episode_links = episode_links[::-1]  # now the episode list is in forward chronological order, (episode_links[0] is first ep, episode_links[1] is second, etc)
    filenames = {episode_links[i]: str(i) for i in range(len(episode_links))}
    # temp = 'https://www.stitcher.com/podcast/michael-moore-4/rumble-with-michael-moore/e/66089075'
    for i in filenames:
        print(i)
        ep_page = requests.get(i)
        ep_page.raise_for_status()
        # soup = bs4.BeautifulSoup(ep_page.text, 'lxml')
        # audio_elem = soup.find('audio', {'id': "jp_audio_0"})
        # print(audio_elem)
        
        ep_url = ep_url_pattern.search(ep_page.text).group(1)
        ep_name = ep_title_pattern.search(ep_page.text).group(1)
        # ep_url = unquote(audio_elem.get('src'))
        print("ep_url: ", ep_url)
        
        # ep_name = soup.find(id="now_playing_title").text
        foldername = f'{target_folder}/{show_name}/'
        filename = f'{filenames[i]} - {ep_name}.mp3'
        print('foldername: ', foldername)
        save_file(foldername, filename, ep_url)
        


# https://anchor.fm/s/10fc9a30/podcast/play/9051653/https%3A%2F%2Fd3ctxlq1ktw2nl.cloudfront.net%2Fproduction%2F2019-11-17%2F39087051-44100-2-9e61f3ca15cf9.mp3
# Ep. 1: Let's Rumble
# //*[@id="now_playing_title"]


def soundcloud_download():
    print('soundcloud dl')

def itunes_download():
    print('itunes dl')

with open('podcast list.txt') as slist:
    podcasts = slist.read().split('\n')
try:
    podcasts.remove('') # gets rid of the empty string that occurs if there are blank lines in the text file
except:
    pass
dest_folder = 'D:/Podcasts/New'

download_podcast(podcasts[0], dest_folder)