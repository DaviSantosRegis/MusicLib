import pytube
from ytmusicapi import YTMusic
from pprint import pprint
import shutil
import requests
from pathlib import Path
from moviepy import editor as me
from pygame import image,transform
import json
import codecs
import time
import sys

ytmusic = YTMusic()

class Downloader():
    def __init__(self,link,folder):
        self.folder = folder
        self.streams = self._get_streams(link)

    def _get_streams(self,link):
        playlist_links = pytube.Playlist(link)
        self._len_playlist = len(playlist_links)
        
        self.already_downloaded_ids = list(map(lambda x:x.name, Path(self.folder).iterdir()))
        
        
        for i, video_link in enumerate(playlist_links):
            
            
            
            print(f"{i+1}/{self._len_playlist} music Playlist")   
            print("Loading",end='\r')
            #The video are already downloaded will return like None 
            self.video = pytube.YouTube(video_link)
            
            print(f"Music Title: {self.video.title}")
            
            IdDownloaded = self.video.video_id in self.already_downloaded_ids
            
            if not IdDownloaded:
                self._start_time = time.time()
                self.music_data = ytmusic.get_song(self.video.video_id)

                self.audio = Audio(self.video)
                self.thumb = Thumb(self.video,self.music_data)
                self.data  = Data(self.music_data)
        
                yield self
            
            else:
                print('Music already downloaded!')
                print()

            
                
    def download(self):
        for i,stream in enumerate(self.streams):
            music_folder = self.folder / stream.audio.video.video_id 

            if not music_folder.exists():
                music_folder.mkdir()

            
            
            print(f"Downloading",end='\r')
            stream.audio.download(music_folder, 'music.mp3')
            stream.thumb.download(music_folder, 'thumb.jpg')
            stream.data.download (music_folder, 'data.json')            

            end_time = time.time()

            delta_time = end_time - self._start_time
            reming_items = self._len_playlist - (i+1)

            eta = delta_time * reming_items
            min , seg = divmod(eta, 60)
            
            
            print(f"Downloaded!")
            print(f"Estimated time to download all musics : {int(min)} min {int(seg)} seg")
            print()
            
            
            
class Audio():
    def __init__(self,video):
        self.video = video
        self.stream = self.video.streams.filter(only_audio=True).last()
    
    def download(self,folder,filename):
        name , wanted_format = filename.split('.')
        origin_format = self.stream.audio_codec

        origin_filename = f"{name}.{origin_format}"
        origin_filepath = self.stream.download(folder,origin_filename)

        NeedCovert = origin_filename != wanted_format
        
        if NeedCovert:
            meaudio = me.AudioFileClip(origin_filepath)
            meaudio.write_audiofile(f"{folder}/{filename}",logger= None)
            
            

class Thumb():
    def __init__(self,video,music_data):
        url = self.get_url(video,music_data)
        self.stream = requests.get(url,stream = True).raw
    
    def get_url(self,video,music_data):
        videoDetails = music_data['videoDetails']
        IsMusic = 'musicVideoType' in videoDetails.keys()
        
        
        if IsMusic:
            musicVideoType = videoDetails['musicVideoType']
            

            #Topic Music
            if musicVideoType == 'MUSIC_VIDEO_TYPE_ATV':
                
                url = videoDetails['thumbnail']['thumbnails'][-1]['url']
                return url
           
        url = video.thumbnail_url
        return url
        
        
    def download(self,folder,filename):
        
        thumb_path = folder / filename
        with open(thumb_path,"wb") as fp:
           shutil.copyfileobj(self.stream,fp)
        
        img = image.load(thumb_path)
        
        if img.get_width() != img.get_height():
            img = img.subsurface((140,60,360,360))
        
        img = transform.scale(img, (300,300))
        image.save(img, thumb_path)

class Data():
    def __init__(self,music_data):
        self.stream = self.get(music_data)

    def get(self,music_data):
        
        videoDetails = music_data['videoDetails']
        
        return {
                'music':{
                            'name': videoDetails['title'],
                            'id': videoDetails['videoId'],
                            'viewsCount': int(videoDetails['viewCount']),
                            'lenghtSeconds': int(videoDetails['lengthSeconds'])
                        },
                'author':{
                            'id':videoDetails['channelId'],
                            'name':videoDetails['author']
                         }
               }
        
                            
    def download(self,folder,filename):
        path = folder / filename
        
        with codecs.open(path,'w',encoding='utf-8') as fp:
            json.dump(self.stream, fp,ensure_ascii=False)
