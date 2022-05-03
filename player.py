from pygame import mixer,image
import pygame
import json
import codecs
from random import shuffle
from pathlib import Path
mixer.init()

class MP3_Player():
    def __init__(self,folder):
        
        self.Music = Music(folder)
        self.Data  = Data(self.Music)
    
    def update(self):
        self.Music.update()
        self.Data.update()
    
class Music():
    def __init__(self,folder):
        
        self.folder = folder
        self.PlaylistId = list(self.folder.iterdir())
        shuffle(self.PlaylistId)
        self.l_PlaylistId = len(self.PlaylistId)
        self.index = 0
        self.add = 0
        self.run()
    
    
    def set_pos(self,pos):
        
        mixer.music.set_pos(pos)
        
        
        self.add += pos - self.Running_Time
        
        
    def run(self):
        self.id = Path(self.PlaylistId[self.index])
        music_path = self.id / 'music.mp3'
        mixer.music.load(music_path)
        self.RunningState = True
        mixer.music.play()
        self.Total_Time = mixer.Sound(music_path).get_length()
    
    def set_music(self,i):
        self.index = i
        self.add = 0
        self.run()

    def next(self):
        
        self.add = 0
        if self.index != self.l_PlaylistId -1:
            self.index += 1
        else:
            self.index = 0
        self.run()
    
    def previous(self):
        self.add = 0

        if self.index != 0:
            self.index -= 1
        else:
            self.index = self.l_PlaylistId - 1
        
        self.run()
    
    def pause_unpause(self):
        if self.RunningState == True:
            mixer.music.pause()
            self.RunningState = False

        else:
            
            mixer.music.unpause()
            self.RunningState = True


    def restart(self):
        mixer.music.set_pos(0)
        self.add = 0
        mixer.music.play()
    

    def update(self):
        self.Running_Time = (mixer.music.get_pos() / 10 ** 3) + self.add
        
        if self.Running_Time == -1 or self.Running_Time >= self.Total_Time:
            self.next()



class Data():
    def __init__(self,music):
        self._music = music
        
    def _img(self):
        img_path = self._music.id / 'thumb.jpg'
        return image.load(img_path)

    def _json(self):
        json_path = self._music.id / 'data.json'
        with codecs.open(json_path,'r',encoding='utf-8') as fp:
            return json.load(fp)

    def update(self):
        
        self.img = self._img()
        self.json = self._json()


