SoundServer (compatible pygame 2.0)
===================================
```
Pygame Sound controller for video game.
SoundServer is a wrapper class (coded with Python & Cython) that simplify pygamne sound scripting.
It allows pygame programer to rely on a very convenient library to control pygame sound objects 
using a set of methods/tools to apply local or global transformations.

It is behaving like an interactive pool of sounds that can be modified from anywhere in your code.

It contains methods such as panning sound effect (not included in pygame 2.0 sound library), 
volume control, sound pause / resume and tools to search for a specific sound(s) that needs 
to be adjusted in your video game.
```

How to initialized the Sound Controller
-----------------------------------------
```python
pygame.mixer.init()
sound1 = pygame.mixer.Sound('Alarm9.ogg')
SCREENRECT = pygame.Rect(0, 0, 800, 1024)
pygame.display.set_mode((SCREENRECT.w, SCREENRECT.h))

# SCREENRECT is a pygame Rect (size of the display and used for the panning mode)
# 8 is the number of channels reserved for the server (behave like a pool of channels)
# When the first channel is busy playing a sound effect, the server automatically select the
# next channel available to load a sound effect.

SND = SoundControl(SCREENRECT, 8)
```

Loading a sound in the Controller 
---------------------------------
```python
# Panning mode:
# Panning is the distribution of a sound signal into a new stereo or multi-channel sound field
# change panning for all sounds being played on the mixer.
# Load a sound without panning mode enable (panning_ = False)

SND.play(sound1, 0, volume_=1.0, panning_=False)

# Panning mode enabled (** pygame mixer must be initialized in stereo mode otherwise the panning effect will be disregarded)
# When panning is selected you must also defined the sound location of a sprite explosion or 
# sound effect on your screen (here 400 pixels in our example). 
# Default location is the screen centre.
# Please see section panning a sound for more details and explanation on how to pan a sound
# right left and vice versa.

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
# milliseconds. 
# The Sound will fade and stop on all actively playing channels.
# Fade-in (int) : The fade_ms argument will make the sound start playing at 0 volume and fade up to full 
# volume over the time given. 
# The sample may end before the fade-in is complete.

SND.play(sound1, -1, volume_=1.0, panning_=True, x_=400, fade_in_ms=200, fade_out_ms=0)

# Naming convention
# The sound controller has various method that can search for a specific sound being played on the mixer.
# After naming a sound object, you will be able to apply search method to find a specific sound from 
# the queue and apply transformation to it or alter similar sound objects.
# You can select a specific name or a unique identifier such as :

sound1 = pygame.mixer.Sound('Alarm9.ogg')
SND.play(sound1, 0, volume_=1.0, panning_=True, x_=400, name_="ALARM")
SND.play(sound1, 0, volume_=1.0, panning_=True, x_=400, object_id_=id(sound1))

```

Panning audio sound
-------------------
```python

# --- Pygame mixer must be initialized in stereo mode otherwise the panning effect will be disregarded. ---

# First option (panning a single sound from the pool by passing a unique identifier to the method 
# "update_sound_panning")
# Use x for the new position of the sound on the display 
# Sound volume at highest intensity 100% -> 1.0
# Define the unique identifier with id_=id(sound1)

x = 0
while 1: 
    pygame.event.pump()
    SND.update_sound_panning(x, 1.0, name_="", id_=id(sound1))
    x += 1
    x %= 1280
    SND.update()
    
# Second option, panning every sounds on the mixer (using the method update_sounds_panning)
# Use x for the new position of the sound on the display 
# Value 1.0 -> sound volume at highest intensity 100%
x = 0
while 1: 
    pygame.event.pump()
    SND.update_sounds_panning(x, 1.0)
    x += 1
    x %= 1280
    SND.update()
    
```

Control sound volume
--------------------
```python
# Use the method update_volume to control the volume (at once) of all the sounds being play by the mixer.
# The effect is immediate for mono and stereo sound effect (panning sound included)

SND.update_volume(0.75) 
```

Pause & resume 
--------------
```python
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

Stop soud(s) various methods
----------------------------
```
Methods : stop, stop_all_excep, stop_all, stop_name, stop_object
```

Searching for a specific sound
------------------------------
```
Methods : get_identical_sounds, get_identical_id
```

Updating the pool
-----------------
```python
# It is a good practice to update the pool every frames to clear every channels when sounds finishes playing.
# The update always take place from the main loop

SND.update()
```

Cython code also available for better performance
-------------------------------------------------

REQUIREMENT:
------------
```
pip install pygame cython numpy==1.19.3

- python > 3.0
- numpy version 1.9.13
- pygame 
- Cython
- A compiler such visual studio, MSVC, CGYWIN setup correctly
  on your system.
  - a C compiler for windows (Visual Studio, MinGW etc) install on your system 
  and linked to your windows environment.
  Note that some adjustment might be needed once a compiler is install on your system, 
  refer to external documentation or tutorial in order to setup this process.
  e.g https://devblogs.microsoft.com/python/unable-to-find-vcvarsall-bat/
```

BUILDING PROJECT:
-----------------
```
In a command prompt and under the directory containing the source files
C:\>python setup_project.py build_ext --inplace

If the compilation fail, refers to the requirement section and make sure cython 
and a C-compiler are correctly install on your system. 
```
