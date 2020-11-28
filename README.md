# SoundServer
Pygame Sound Server for video game

## HOW TO INITIALIZED THE SOUND SERVER
```
pygame.mixer.init()
sound1 = pygame.mixer.Sound('Alarm9.ogg')
SCREENRECT = pygame.Rect(0, 0, 800, 1024)
pygame.display.set_mode((SCREENRECT.w, SCREENRECT.h))

# SCREENRECT is a pygame Rect (size of the display and used for the panning mode)
# 8 is the channel number reserved for the server (behave like a pool of channels)
# When the first channel is busy playing a sound effect the server use the next channel available.
SND = SoundControl(SCREENRECT, 8)
```
