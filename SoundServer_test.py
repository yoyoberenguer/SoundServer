
import pygame
from SoundServer import SoundControl

if __name__ == "__main__":

    pygame.mixer.init()
    sound1 = pygame.mixer.Sound('Alarm9.ogg')
    SCREENRECT = pygame.Rect(0, 0, 800, 1024)
    pygame.display.set_mode((SCREENRECT.w, SCREENRECT.h))
    SND = SoundControl(SCREENRECT, 8)
    # SND.play(sound1, -1, volume_=1.0, panning_=False)
    SND.play(sound1, -1, volume_=1.0, panning_=True, x_=200, fade_in_ms=100, fade_out_ms=100)
    # SND.play(sound1, -1, volume_=1.0, panning_=True, x_=100)
    # SND.play(sound1, -1, volume_=1.0, panning_=True, x_=200)
    # SND.play(sound1, -1, volume_=1.0, panning_=True, x_=400)
    # SND.play(sound1, -1, volume_=1.0, panning_=True, x_=800)
    # SND.play(sound1, -1, volume_=1.0, panning_=True, x_=100)
    # SND.play(sound1, -1, volume_=1.0, panning_=True, x_=450)
    x = 0
    v = 1.0
    FRAME = 0
    while 1:
        # SND.show_sounds_playing()
        pygame.event.pump()
        pygame.display.flip()
        # SND.update_sounds_panning(x, v)

        # SND.update_sound_panning(x, 0.1, None, id(sound1))
        if x < SCREENRECT.w:
            SND.update_sound_panning(x, 0.2, None, id(sound1))
            x += 0.1
        else:
            SND.update_volume(1)

        SND.update()
        if 4000 < FRAME < 9000:
            SND.pause_sounds()
        else:
            SND.unpause_sound(id_=id(sound1))
        SND.show_free_channels()
        SND.show_sounds_playing()
        # print(SND.return_time_left(id(sound1)))
        print(FRAME)
        if FRAME == 1000:
            SND.stop_all()

        #print(SND.get_identical_sounds(sound1))
        #print(SND.get_identical_id(id(sound1)))



        #x += 1
        #x %= SCREENRECT.w
        FRAME += 1
