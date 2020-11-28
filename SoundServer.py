# encoding: utf-8


__version__ = "1.0.1"


try:
    import pygame
    from pygame import mixer
except ImportError:
    raise ImportError("\n<pygame> library is missing on your system."
          "\nTry: \n   C:\\pip install pygame on a window command prompt.")


from time import time


class SoundObject:

    def __init__(self, sound_, priority_: int, name_: str,
                 channel_: int, obj_id_: int, position_: int, loop_: int = False):
        """
        CREATE A SOUND OBJECT CONTAINING CERTAIN ATTRIBUTES (SEE THE
        COMPLETE LIST BELOW)

        :param sound_   : Sound object; Sound object to play
        :param priority_: integer; Define the sound priority (Sound with highest priority have to be stopped with
                          specific methods)
        :param name_    : string; Sound given name (if the object has no name -> str(id(sound_))
        :param channel_ : integer; Channel to use (channel where the sound is being played by the mixer)
        :param obj_id_  : python int (C long long int); Sound unique ID
        :param position_: integer | None ; Sound position for panning sound in stereo.
                          position must be within range [0...Max display width]
        :param loop_    : int; -1 for looping the sound
        """
        self.sound          = sound_                                 # sound object to play
        self.length         = sound_.get_length()                    # return the length of this sound in seconds
        self.priority       = priority_ if 0 < priority_ < 2 else 0  # sound priority - lowest to highest (0 - 2)
        self.time           = time()                                 # timestamp
        self.name           = name_                                  # sound name for identification
        self.active_channel = channel_                               # channel used
        self.obj_id         = obj_id_                                # unique sound id number
        self.id             = id(self)                               # class id

        # NOTE : new attribute 27/11/2020
        # sound position for panning sound on stereo

        self.pos            = position_                              # Sound position for panning method
        self.loop           = loop_


class SoundControl(object):

    def __init__(self, screen_size_, channels_: int = 8):
        """

        :param screen_size_: pygame.Rect; Size of the active display
        :param channels_   : integer; number of channels to reserved for the sound controller
        :return            : None
        """

        if not isinstance(screen_size_, pygame.Rect):
            raise ValueError("\n screen_size_ argument must be a pygame.Rect type, got %s " % type(screen_size_))
        if not isinstance(channels_, int):
            raise ValueError("\n channels_ argument must be a integer type, got %s " % type(channels_))

        assert channels_ >= 1, "\nArgument channel_num_ must be >=1"

        if pygame.mixer.get_init() is None:
            raise ValueError("\nMixer has not been initialized."
                             "\nUse pygame.mixer.init() before starting the Sound controller")

        self.channel_num = channels_                            # channel to init
        self.start       = mixer.get_num_channels()             # get the total number of playback channels
        self.end         = self.channel_num + self.start        # last channel
        mixer.set_num_channels(self.end)                        # sets the number of available channels for the mixer.
        mixer.set_reserved(self.end)                            # reserve channels from being automatically used
        self.channels    = [mixer.Channel(j + self.start)
                            for j in range(self.channel_num)]   # create a channel object for controlling playback
        self.snd_obj     = [None] * self.channel_num            # list of un-initialised objects
        self.channel = self.start                               # pointer to the bottom of the stack
        self.all = list(range(self.start, self.end))            # create a list with all channel number
        self.screen_size = screen_size_                         # size of the display (used for stereo mode)

    def update(self):
        """
        THIS METHOD HAS TO BE CALLED FROM THE MAIN LOOP OF YOUR PROGRAM
        DETECT SOUNDS THAT HAVE STOPPED TO PLAY ON THE MIXER AND SET THE CHANNEL VALUE TO NONE
        """
        i = 0
        snd_obj = self.snd_obj

        for c in self.channels:
            if c:
                # Returns True if the mixer is busy mixing any channels.
                # If the mixer is idle then this return False.
                if not c.get_busy():
                    snd_obj[i] = None
            i += 1

    # SINGLE SOUND
    def update_sound_panning(self, new_x_: int, volume_: float, name_=None, id_=None) -> None:

        """
        PANNING IS THE DISTRIBUTION OF A SOUND SIGNAL INTO A NEW STEREO OR MULTI-CHANNEL SOUND FIELD
        CHANGE PANNING FOR ALL SOUNDS BEING PLAYED ON THE MIXER.

        ADJUST THE PANNING OF A GIVEN SOUND (FOUND THE SOUND OBJECT WITH AN EXPLICIT NAME OR ID).
        AT LEAST ONE SEARCH METHOD MUST BE DEFINED.

        :param new_x_  : integer; new sound position in the display. Value must be in range [0, Max width]
        :param volume_ : float; Sound volume (adjust all sound being played by the mixer)
                         value must be in range [0 ... 1.0]
        :param name_   : string; Given sound name (name given at the time eof the SoundObject construction)
        :param id_     : int | None; Default None. ID number such as object_id_ = id(sound_).
        :return        : None

        """
        assert 0 <= new_x_ <= self.screen_size.w, \
            "\nArgument new_x_ value must be in range (0, %s) got %s" % (self.screen_size.w, new_x_)

        # SET THE VOLUME IN CASE OF AN INPUT ERROR
        if 0.0 >= volume_ >= 1.0:
            volume_ = 1.0

        if name_ is None and id_ is None:
            raise ValueError("\nInvalid function call, at least one argument must be set!")

        # search by name take precedence (if name value is not undefined)
        if name_ is not None:
            id_ = None

        # Calculate the sound panning, left & right volume values
        left, right = self.stereo_panning(new_x_, self.screen_size.w)
        left *= volume_
        right *= volume_

        channels = self.channels  # Fetch all the channels from the sound controller

        for obj in self.snd_obj:  # Iterate all the SoundObject
            if obj:
                if hasattr(obj, "pos") and obj.pos is not None:
                    # search by name
                    if name_ is not None:

                        if hasattr(obj, 'name') and hasattr(obj, 'active_channel'):
                            if obj.name == name_:
                                c = obj.active_channel  # Channel playing the sound
                                obj.pos = new_x_        # update the sound position
                                try:
                                    channel = channels[c]
                                    if hasattr(channel, 'set_volume'):
                                        channel.set_volume(left, right)  # set the panning for the channel
                                    else:
                                        raise AttributeError("\nObject is missing attribute set_volume")
                                except IndexError as e:
                                    raise IndexError("\n %s " % e)
                            else:
                                continue
                        else:
                            raise IndexError(
                                "\nSoundObject is missing attribute(s), "
                                "obj must be a SoundObject type got %s " % type(obj))

                    # search by id
                    elif id_ is not None:
                        if hasattr(obj, 'obj_id') and hasattr(obj, 'active_channel'):
                            if obj.obj_id == id_:
                                c = obj.active_channel  # Channel playing the sound
                                obj.pos = new_x_        # update the sound position
                                try:
                                    channel = channels[c]
                                    if hasattr(channel, 'set_volume'):
                                        channel.set_volume(left, right)  # set the panning for the channel
                                    else:
                                        raise AttributeError("\nObject is missing attribute set_volume")
                                except IndexError as e:
                                    raise IndexError("\n %s " % e)
                            else:
                                continue
                    else:
                        print('\nFunction call error, at least one search method must'
                              ' be set (search by name or search by id')
                        return

    # ALL SOUNDS
    def update_sounds_panning(self, new_x_: int, volume_: float) -> None:
        """
        PANNING IS THE DISTRIBUTION OF A SOUND SIGNAL INTO A NEW STEREO OR MULTI-CHANNEL SOUND FIELD
        CHANGE PANNING FOR ALL SOUNDS BEING PLAYED ON THE MIXER.

        THIS METHOD ITERATE OVER ALL SOUNDS BEING PLAYED BY THE MIXER AND ADJUST THE PANNING ACCORDING
        TO THE NEW POSITION new_x_ AND GIVEN VOLUME_

        :param new_x_  : integer; new sound position in the display. Value must be in range [0, Max width]
        :param volume_ : float; Sound volume (adjust all sound being played by the mixer)
                         value must be in range [0 ... 1.0]
        :return        : None

        """
        assert 0 <= new_x_ <= self.screen_size.w, \
            "\nArgument new_x_ value must be in range (0, %s) got %s" % (self.screen_size.w, new_x_)

        # SET THE VOLUME IN CASE OF AN INPUT ERROR
        if 0.0 >= volume_ >= 1.0:
            volume_ = 1.0

        # Calculate the sound panning, left & right volume values
        left, right = self.stereo_panning(new_x_, self.screen_size.w)
        left  *= volume_
        right *= volume_

        channels = self.channels    # Fetch all the channels from the sound controller

        for obj in self.snd_obj:    # Iterate all the SoundObject
            if obj:
                if hasattr(obj, "pos") and obj.pos is not None:
                    if hasattr(obj, 'active_channel'):
                        c = obj.active_channel                # Channel playing the sound
                        obj.pos = new_x_                      # update the sound position
                        try:
                            c = channels[c]
                            if hasattr(c, "set_volume"):
                                c.set_volume(left, right)   # set the panning for the channel
                            else:
                                raise AttributeError('\nObject is missing attributes set_volume')
                        except IndexError as e:
                            raise IndexError("\n %s " % e)
                    else:
                        raise AttributeError(
                            "\nSoundObject is missing attribute(s), "
                            "obj must be a SoundObject type got %s " % type(obj))

    def update_volume(self, volume_: float = 1.0) -> None:
        """
        UPDATE ALL SOUND OBJECT VOLUME TO A SPECIFIC VALUE.
        THIS HAS IMMEDIATE EFFECT AND DO NOT FADE THE SOUND

        AFFECT ALL SOUNDS WITH OR WITHOUT PANNING EFFECT.
        PANNING SOUND EFFECT WILL BE CONSERVED AFTER ADJUSTING THE VOLUME

        :param volume_: float; volume value, default is 1.0
        :return       : None
        """
        # SET THE VOLUME IN CASE OF AN INPUT ERROR
        if 0.0 >= volume_ >= 1.0:
            volume_ = 1.0

        objs = self.snd_obj
        i = 0
        # SET THE VOLUME FOR ALL SOUNDS
        for channel in self.channels:

            try:
                single_obj = objs[i]
            except IndexError as e:
                raise IndexError("\n %s " % e)

            if single_obj is not None:

                # WITH PANNING
                if hasattr(single_obj, "pos") and single_obj.pos is not None:
                    if hasattr(channel, "set_volume"):
                        # Calculate the sound panning, left & right volume values
                        left, right = self.stereo_panning(single_obj.pos, self.screen_size.w)
                        left *= volume_
                        right *= volume_
                        channel.set_volume(left, right)

                # WITHOUT PANNING
                else:
                    if single_obj is not None:
                        if hasattr(single_obj.sound, "set_volume"):
                            single_obj.sound.set_volume(volume_)

            i += 1

    def pause_sound(self, name_: str = None, id_=None) -> None:
        """
        PAUSE A SINGLE SOUND FROM THE MIXER (AT LEAST ONE SEARCH ELEMENT HAS TO BE PROVIDED NAME OR ID)

        :param name_   : string | None; Given sound name (name given at the time eof the SoundObject construction)
        :param id_     : int | None; Default None. ID number such as object_id_ = id(sound_).
        :return        : None
        """
        if name_ is None and id_ is None:
            raise ValueError("\nInvalid function call, at least one argument must be set!")
        # search by name take precedence (if name value is not undefined)
        if name_ is not None:
            id_ = None

        objs = self.snd_obj
        i = 0
        # SET THE VOLUME FOR ALL SOUNDS
        for channel in self.channels:
            if hasattr(channel, "pause"):
                try:
                    single_obj = objs[i]
                except IndexError as e:
                    raise IndexError("\n %s " % e)

                if single_obj is not None:

                    # search by name
                    if name_ is not None:
                        if single_obj.name == name_:
                            channel.pause()

                    # search by id_
                    elif id_ is not None:
                        if single_obj.obj_id == id_:
                            channel.pause()

            i += 1
        ...

    def pause_sounds(self) -> None:
        """
        PAUSE ALL SOUND OBJECTS (THIS HAS IMMEDIATE EFFECT)

        :return       : None
        """

        objs = self.snd_obj
        i = 0
        # SET THE VOLUME FOR ALL SOUNDS
        for channel in self.channels:

            try:
                single_obj = objs[i]
            except IndexError as e:
                raise IndexError("\n %s " % e)

            if single_obj is not None:

                if hasattr(channel, "pause"):
                    channel.pause()
            i += 1

    def unpause_sounds(self) -> None:
        """
        UNPAUSE ALL SOUND OBJECTS (THIS HAS IMMEDIATE EFFECT)

        :return       : None
        """

        objs = self.snd_obj
        i = 0

        for channel in self.channels:

            try:
                single_obj = objs[i]
            except IndexError as e:
                raise IndexError("\n %s " % e)

            if single_obj is not None:
                if hasattr(channel, "unpause"):
                    channel.unpause()
            i += 1

    def unpause_sound(self, name_: str = None, id_=None) -> None:
        """
        UNPAUSE A SINGLE SOUND FROM THE MIXER (AT LEAST ONE SEARCH ELEMENT HAS TO BE PROVIDED NAME OR ID)

        :param name_   : string | None; Given sound name (name given at the time eof the SoundObject construction)
        :param id_     : int | None; Default None. ID number such as object_id_ = id(sound_).
        :return        : None
        """

        if name_ is None and id_ is None:
            raise ValueError("\nInvalid function call, at least one argument must be set!")

        # search by name take precedence (if name value is not undefined)
        if name_ is not None:
            id_ = None

        objs = self.snd_obj
        i = 0

        for channel in self.channels:

            try:
                single_obj = objs[i]
            except IndexError as e:
                raise IndexError("\n %s " % e)

            if single_obj is not None:
                # search by name
                if name_ is not None:
                    if single_obj.name == name_:
                        channel.unpause()

                # search by id_
                elif id_ is not None:
                    if single_obj.obj_id == id_:
                        channel.unpause()

            i += 1

    def show_free_channels(self) -> list:
        """
        RETURN A LIST OF FREE CHANNELS (NUMERICAL VALUES).
        :return: list; RETURN A LIST
        """

        free_channels = []
        i = 0
        free_channels_append = free_channels.append
        start = self.start

        for c in self.channels:
            if not c.get_busy():
                free_channels_append(i + start)
            i += 1
        print("Free channels : %s " % free_channels)

        return free_channels

    def show_sounds_playing(self):
        """
        DISPLAY ALL SOUNDS OBJECTS
        """
        j = 0
        for object_ in self.snd_obj:
            if object_:
                timeleft = round(object_.length - (time() - object_.time), 2)
                # if timeleft < 0, most likely to be a sound with attribute loop enabled
                if timeleft < 0.0:
                    timeleft = 0.0
                print('Name %s priority %s  channel %s length(s) %s time left(s) %s' %
                      (object_.name, object_.priority, object_.active_channel, round(object_.length, 2),
                       timeleft))

            j += 1

    def get_identical_sounds(self, sound_: pygame.mixer.Sound) -> list:
        """
        RETURN A LIST OF CHANNEL(S) PLAYING IDENTICAL SOUND OBJECT(s)
        SEARCH BY IDENTICAL PYGAME.SOUND OBJECT

        :param sound_ : Mixer object; Object to compare to
        :return      : python list; List containing channels number playing similar sound object,
                       if no match is found, return an empty list
        """
        assert isinstance(sound_, pygame.mixer.Sound), \
            "\nPositional argument sound_ must be a pygame.mixer.Sound type, got %s " % type(sound_)
        duplicate = []
        duplicate_append = duplicate.append

        for obj in self.snd_obj:
            if obj:
                if obj.sound == sound_:
                    duplicate_append(obj.active_channel)
        return duplicate

    def get_identical_id(self, id_: int) -> list:
        """
        RETURN A LIST CONTAINING ANY IDENTICAL SOUND BEING MIXED.
        USE THE UNIQUE ID FOR REFERENCING OBJECTS

        :param id_: python integer; unique id number that reference a sound object
        :return   : list; Return a list of channels containing identical sound object
        """
        assert isinstance(id_, int), \
            "\nPositional argument id_ must be an int type, got %s " % type(id_)
        duplicate = []
        duplicate_append = duplicate.append

        for obj in self.snd_obj:
            if obj:
                if obj.obj_id == id_:
                    duplicate_append(obj)
        return duplicate

    def stop(self, stop_list_: list):
        """
        STOP ALL SOUND BEING PLAYED ON THE GIVEN LIST OF CHANNELS.
        ONLY SOUND WITH PRIORITY LEVEL 0 CAN BE STOPPED.

        :param stop_list_: python list; list of channels
        :return         : None
        """
        assert isinstance(stop_list_, list), \
            "\nPositional argument stop_list must be a python list type, got %s " % type(stop_list_)
        start = self.start
        snd_obj = self.snd_obj
        channels = self.channels

        for c in stop_list_:
                l = c - start
                if snd_obj[l]:
                    if snd_obj[l].priority == 0:
                        channels[l].set_volume(0.0, 0.0)
                        channels[l].stop()
        self.update()

    def stop_all_except(self, exception_: list):
        """
        STOP ALL SOUND OBJECT EXCEPT SOUNDS FROM A GIVEN LIST OF ID(SOUND)
        IT WILL STOP SOUND PLAYING ON ALL CHANNELS REGARDLESS
        OF THEIR PRIORITY.

        :param exception_: Can be a single pygame.Sound id value or a list containing
                           all pygame.Sound object id numbers.
        """

        assert isinstance(exception_, list),\
            "\nPositional argument exception_ must be a python list type, got %s " % type(exception_)

        start = self.start
        snd_obj = self.snd_obj
        channels = self.channels

        for c in self.all:
            l = c - start
            snd_object = snd_obj[l]
            if snd_object:
                if snd_object.obj_id not in exception_:
                    channels[l].set_volume(0.0)
                    channels[l].stop()
        self.update()

    def stop_all(self):
        """
        STOP ALL SOUNDS NO EXCEPTIONS.

        :return: None
        """

        start = self.start
        snd_obj = self.snd_obj
        channels = self.channels

        for c in self.all:
            l = c - start
            snd_object = snd_obj[l]
            if snd_object:
                channels[l].set_volume(0.0)
                channels[l].stop()
        self.update()

    def stop_name(self, name_: str = ""):
        """
        STOP A PYGAME.SOUND OBJECT IF PLAYING ON ANY OF THE CHANNELS.
        :param name_: string; Sound name to stop
        :return     :  None
        """
        assert isinstance(name_, str),\
            "\nPositional argument name_ must be a python string type, got %s " % type(name_)
        channels = self.channels
        start = self.start

        for sound in self.snd_obj:
            if sound and sound.name == name_:
                try:
                    channels[sound.active_channel - start].set_volume(0.0)
                    channels[sound.active_channel - start].stop()
                except IndexError:
                    # IGNORE ERROR
                    ...
        self.update()

    def stop_object(self, object_id: int):
        """
        STOP A GIVEN SOUND USING THE PYGAME.SOUND OBJECT ID NUMBER.

        :param object_id: integer; Object unique identifier such as id(sound)
        :return         : None
        """
        assert isinstance(object_id, int), \
            "\nPositional argument object_id must be a python string type, got %s " % type(object_id)

        channels = self.channels
        start = self.start

        for sound in self.snd_obj:
            if sound and sound.obj_id == object_id:
                try:
                    channels[sound.active_channel - start].set_volume(0.0)
                    channels[sound.active_channel - start].stop()
                except IndexError:
                    # IGNORE ERROR
                    ...

        self.update()

    def return_time_left(self, object_id) -> float:
        """
        RETURN THE TIME LEFT IN SECONDS (RETURN -1 IF SOUND IS SEAMLESS LOOPED ON THE CHANNEL,
        AND NONE WHEN SOUND IS NOT FOUND

        :param object_id: python integer; unique object id
        :return         : float | None; Return a float representing the time left in seconds.
        """
        j = 0
        snd_obj = self.snd_obj
        for obj in snd_obj:
            if obj:
                if obj.obj_id == object_id:
                    timeleft = round(snd_obj[j].length - (time() - snd_obj[j].time), 2)
                    # if timeleft < 0, most likely to be a sound with attribute loop enabled
                    if timeleft < 0.0:
                        if obj.loop:
                            return -1.0
                    else:
                        timeleft = 0.0
                    return timeleft
            j += 1
        return None

    def get_reserved_channels(self):
        """ RETURN THE NUMBER OF RESERVED CHANNELS """
        return self.channel_num

    def get_reserved_start(self):
        """ RETURN THE FIRST RESERVED CHANNEL NUMBER """
        return self.start

    def get_reserved_end(self):
        """ RETURN THE LAST RESERVED CHANNEL NUMBER """
        return self.end

    def get_channels(self):
        """
        RETURN A LIST OF ALL RESERVED PYGAME MIXER CHANNELS.
        """
        return self.channels

    def get_sound(self, channel_):
        """
        RETURN THE SOUND BEING PLAYED ON A SPECIFIC CHANNEL (PYGAME.MIXER.CHANNEL)

        :param channel_: integer;  channel_ is an integer representing the channel number.
        """
        try:
            sound = self.channels[channel_]
        except IndexError:
            raise Exception('\nIndexError: Channel number out of range ')
        else:
            return sound

    def get_sound_object(self, channel_):
        """
        RETURN A SPECIFIC SOUND OBJECT
        RETURN NONE IN CASE OF AN INDEX ERROR
        """
        try:
            s = self.snd_obj[channel_]
        except IndexError:
            return None
        else:
            return s

    def get_all_sound_object(self):
        """ RETURN ALL SOUND OBJECTS """
        return self.snd_obj

    def play(self, sound_, loop_=0, priority_=0, volume_=1.0,
             fade_in_ms=100, fade_out_ms=100, panning_=False, name_=None,
             x_=None, object_id_=None):

        """
        PLAY A SOUND OBJECT ON THE GIVEN CHANNEL
        RETURN NONE IF ALL CHANNELS ARE BUSY OR IF AN EXCEPTION IS RAISED


        :param sound_       : pygame mixer sound
        :param loop_        : loop the sound indefinitely -1 (default = 0)
        :param priority_    : Set the sound priority (low : 0, med : 1, high : 2)
        :param volume_      : Set the sound volume 0.0 to 1.0 (100% full volume)
        :param fade_in_ms   : Fade in sound effect in ms
        :param fade_out_ms  : float; Fade out sound effect in ms
        :param panning_     : boolean for using panning method (stereo mode)
        :param name_        : String representing the sound name (if no name default is -> str(id(sound_)))
        :param x_           : Sound position for stereo mode,
        :param object_id_   : unique sound id
        """

        l            = 0
        channels     = self.channels
        channel      = self.channel
        start        = self.start
        end          = self.end
        screen_width = self.screen_size.w

        left  = 0
        right = 0

        try:
            if not sound_:
                raise AttributeError('\nIncorrect call argument, sound_ cannot be None')

            if panning_:
                # panning mode is enable but sound position value is not correct
                # Adjusting the value manually
                if x_ is None or (0 > x_ > screen_width):
                    x_ = screen_width >> 1
            # Regardless x_ value, if passing mode is disabled the variable
            # x_ is set to None
            else:
                x_ = None

            # set a name by default id(sound_)
            if name_ is None:
                name_ = str(id(sound_))

            # set object id default value
            if object_id_ is None:
                object_id_ = id(sound_)

            l = channel - start
            # TODO OVERFLOW CHANNELS[l]
            # CHECK IF CURRENT CHANNEL IS BUSY
            if channels[l].get_busy() == 0:

                # PLAY A SOUND IN STEREO MODE
                if panning_:
                    left, right = self.stereo_panning(x_, self.screen_size.w)
                    channels[l].set_volume(left * volume_, right * volume_)

                else:
                    channels[l].set_volume(volume_)

                channels[l].fadeout(fade_out_ms)
                channels[l].play(sound_, loops=loop_, maxtime=0, fade_ms=fade_in_ms)

                self.snd_obj[l] = SoundObject(sound_, priority_, name_, l, object_id_, position_ = x_, loop_ = loop_)

                # PREPARE THE MIXER FOR THE NEXT CHANNEL
                self.channel += 1

                if self.channel > end - 1:
                    self.channel = start

                # RETURN THE CHANNEL NUMBER PLAYING THE SOUND OBJECT
                return channel - 1

            # ALL CHANNELS ARE BUSY
            else:
                self.stop(self.get_identical_sounds(sound_))
                # VERY IMPORTANT, GO TO NEXT CHANNEL.
                self.channel += 1
                if self.channel > end - 1:
                    self.channel = start
                return None

        except IndexError as e:
            print('\n[-] SoundControl error : %s ' % e)
            print(self.channel, l)
            return None

    def display_size_update(self, rect_):
        """
        UPDATE THE SCREEN SIZE AFTER CHANGING MODE
        THIS FUNCTION IS MAINLY USED FOR THE PANNING MODE (STEREO)
        :param rect_: pygame.Rect; display dimension
        :return: None
        """
        self.screen_size = rect_

    def stereo_panning(self, x_, screen_width):
        """
        STEREO MODE

        :param screen_width: display width
        :param x_          : integer; x value of sprite position on screen
        :return: tuple of float;
        """
        right_volume = 0.0
        left_volume  = 0.0

        # MUTE THE SOUND IF OUTSIDE THE BOUNDARIES
        if 0 > x_ > screen_width:
            return right_volume, left_volume

        right_volume = float(x_) / screen_width
        left_volume  = 1.0 - right_volume

        return left_volume, right_volume


