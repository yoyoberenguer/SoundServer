# SoundServer
Pygame Sound Server for video game

## HOW TO INITIALIZED THE SOUND SERVER
```
pygame.mixer.init()
sound1 = pygame.mixer.Sound('Alarm9.ogg')
SCREENRECT = pygame.Rect(0, 0, 800, 1024)
pygame.display.set_mode((SCREENRECT.w, SCREENRECT.h))

SND = SoundControl(SCREENRECT, 8)
```
