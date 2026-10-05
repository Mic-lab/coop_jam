import os
import pygame

pygame.mixer.init()

SOUNDS_DIR = os.path.join('data/sfx/sounds')
MUSIC_DIR = os.path.join('data/sfx/music')

def play_music(file_name, *args, loops=-1, **kwargs):
    return
    # Program freezes when there's music.fadeout
    # So for the music to forcefully play, the fadout must be stopped. 
    pygame.mixer.music.stop()
    pygame.mixer.music.load(os.path.join(MUSIC_DIR, file_name))
    pygame.mixer.music.play(*args, loops=loops, **kwargs)

def load_sounds():
    print('Loading sounds...')
    sounds = {}
    for file in os.listdir(SOUNDS_DIR):
        full_file = os.path.join(SOUNDS_DIR, file)
        sound = pygame.mixer.Sound(full_file)
        print(f'Loading {file}')

        if file == 'pop.wav':
            v = 0.4
        elif file.startswith('kill'):
            v = 1
        elif file.startswith('hit.wav'):
            v = 0.7
        elif file.startswith('select.wav'):
            v = 1
        elif file.startswith('double_jump'):
            v = 1
        elif file.startswith('jump'):
            v = 1
        elif 'combo' in file:
            v = 0.9
        elif file == 'pickup.wav':
            v = 0.3
        else:
            v = 0.6


        sound.set_volume(v)

        sounds[file] = sound
    return sounds

def init_custom_music():
    pygame.mixer.set_reserved(0)

def play_custom_music(sound, loops=-1):
    pygame.mixer.Channel(0).play(sound, loops)

sounds = load_sounds()


