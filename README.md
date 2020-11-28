# SoundServer

Pygame Sound Server for video game.
This library control sound effects for your video game. 
No need to control every single sound played in your game,  pass the sound to the Sound controller and apply
transformation to all at once or to specific sound(s).
It contains methods such as panning sound effect (not included in pygame 2.0), volume control, pause and resume and tools 
to locate specific sound(s) that needs adjusting.


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
# What is the panning mode:
# Panning is the distribution of a sound signal into a new stereo or multi-channel sound field
# change panning for all sounds being played on the mixer.
# Load a sound without panning mode (panning_ = False)

SND.play(sound1, 0, volume_=1.0, panning_=False)

# Panning mode enabled.
# When panning is selected you must also defined the sound location on the display (here 400 pixels), 
# otherwise the middle of the display will be choosen by default.

SND.play(sound1, 0, volume_=1.0, panning_=True, x_=400)

# Repeating a sound over and over 
# The loops argument controls how many times the sample will be repeated after being played the first time. 
# A value of 5 means that the sound will be played once, then repeated # five times, and so is played a total 
# of six times. The default value (zero) means the Sound is not repeated, and so is only played once. 
# If loops is set to -1 the Sound will # loop indefinitely (though you can still call stop() to stop it).
# DEFAULT Value is 0 (Sound is not repeated)

SND.play(sound1, loop_=-1, volume_=1.0, panning_=True, x_=400)  # here sound will be play indefinately 

# Sound & volume control 
# Volume must be a float in range [0.0 ... 1.0]. Incorrect values will be adjusted to 1.0 (default value).
# Below an example of volume at 50% of the maximum gain

SND.play(sound1, loop_=-1, volume_=0.5, panning_=True, x_=400)

# Fade in and fade out effect 
# fade-out (int): This will stop playback of the sound after fading it out over the time argument in 
milliseconds. 
# The Sound will fade and stop on all actively playing channels.
# Fade-in (int) : The fade_ms argument will make the sound start playing at 0 volume and fade up to full 
# volume over the time given. 
# The sample may end before the fade-in is complete.

SND.play(sound1, -1, volume_=1.0, panning_=True, x_=400, fade_in_ms=200, fade_out_ms=0)

# Naming convention
# The sound controller has various method that can search for a specific sound being played on the mixer.
# You can select a specific name or a unique identifier such as :

sound1 = pygame.mixer.Sound('Alarm9.ogg')
SND.play(sound1, 0, volume_=1.0, panning_=True, x_=400, name_="ALARM")
SND.play(sound1, 0, volume_=1.0, panning_=True, x_=400, object_id_=id(sound1))

```

## Panning audio sound
```
# First option (panning a single sound from the pool by passing a unique identifier to the method 
"update_sound_panning")
# Use x for the new position of the sound on the display 
# Sound volume at highest intensity 100% -> 1.0
# Define the unique identifier with id_=id(sound1)

x = 0
while 1: 
    pygame.event.pumpt()
    SND.update_sound_panning(x, 1.0, name_="", id_=id(sound1))
    x += 1
    x %= 1280
    
# Second option, panning every sounds on the mixer (using the method update_sounds_panning)
# Use x for the new position of the sound on the display 
# Value 1.0 -> sound volume at highest intensity 100%
x = 0
while 1: 
    pygame.event.pumpt()
    SND.update_sounds_panning(x, 1.0)
    x += 1
    x %= 1280
    
```

## Control sound volume
```
# Use the method update_volume to control the volume (at once) of all the sounds being play by the mixer.
# The effect is immediate for mono and stereo sound effect (panning sound included)

SND.update_volume(0.75) 
```

## Pause & resume 
```
# PAUSE
# Method pause_sound to pause a single sound effect
# Method pause_sounds to pause all sounds being play on the mixer

# RESUME
# Method unpause_sound for a single sound effect
# Method unpause_sounds for all sounds being play on the mixer

# e.g

# pause all sounds
if FRAME == 200:
    SND.pause_sounds()
    
# resume sound with id = id(sound1)
if FRAME == 400:
    SND.unpause_sound(id_=id(sound1))
```

## Stop soud(s) various methods
```
Methods : stop, stop_all_excep, stop_all, stop_name, stop_object
```

## Searching for a specific sound 
```
Methods : get_identical_sounds, get_identical_id
```

## Updating the pool
```
# It is a good practice to update the pool every frames to clear every channels when sounds finishes playing.
# The update always take place from the main loop
SND.update()
```
