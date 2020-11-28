# SoundServer
Pygame Sound Server for video game

## How to initialized the Sound Controller
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

## Loading a sound in the Controller 
```
What is the panning mode:
Panning is the distribution of a sound signal into a new stereo or multi-channel sound field
change panning for all sounds being played on the mixer.

# Load a sound without panning mode (panning_ = False)
SND.play(sound1, -1, volume_=1.0, panning_=False)

# Panning mode enabled.
# When panning is selected you must also defined the sound location on the display (here 400 pixels), 
# otherwise the middle of the display will be choosen by default.
SND.play(sound1, -1, volume_=1.0, panning_=True, x_=400)
```
