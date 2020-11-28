# encoding: utf-8

__version__ = "1.0.1"

try:
    import pygame
    from pygame import mixer
except ImportError:
    raise ImportError("\n<pygame> library is missing on your system."
          "\nTry: \n   C:\\pip install pygame on a window command prompt.")

from libc.stdio cimport printf

try:
    cimport cython
    from cpython.list cimport PyList_Append, PyList_GetItem, PyList_Size, PyList_SetItem
    from cpython.object cimport PyObject_SetAttr
    from cpython cimport PyObject, PyObject_HasAttr, PyObject_IsInstance
    from cpython cimport array
except ImportError:
    raise ImportError("\n<cython> library is missing on your system."
          "\nTry: \n   C:\\pip install cython on a window command prompt.")

from time import time

cdef struct stereo:
   float left;
   float right;

@cython.boundscheck(False)
@cython.wraparound(False)
@cython.nonecheck(False)
@cython.cdivision(True)
cdef class SoundObject(object):

    cdef:
        public sound
        public int priority, length, active_channel, loop
        public long int time,
        public str name
        public long long int obj_id, id
        public object pos

    # Sound player constructor
    def __init__(self, sound_, int priority_, str name_,
                 int channel_, long long int obj_id_, object position_, int loop_ = False):
        """
        CREATE A SOUND OBJECT CONTAINING CERTAIN ATTRIBUTES (SEE THE
        COMPLETE LIST BELOW)

        :param sound_   : Sound object; Sound object to play
        :param priority_: integer; Define the sound priority (Sound with highest priority have to be stopped with
                          specific methods)
        :param name_    : string; Sound given name (if the object has no name -> str(id(sound_))
        :param channel_ : integer; Channel to use (channel where the sound is being played by the mixer)
        :param obj_id_  : python int (C long long int); Sound unique ID
        :param position_: object ; Sound position for panning sound in stereo.
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


@cython.boundscheck(False)
@cython.wraparound(False)
@cython.nonecheck(False)
@cython.cdivision(True)
cdef class SoundControl(object):

    cdef:
        public int channel_num, start, end, channel
        public list channels, snd_obj, all
        public screen_size


    def __init__(self, screen_size_, int channels_=8):

        """

        :param screen_size_: pygame.Rect; Size of the active display
        :param channels_   : integer; number of channels to reserved for the sound controller
        :return            : None
        """
        if not PyObject_IsInstance(screen_size_, pygame.Rect):
            raise ValueError("\n screen_size_ argument must be a pygame.Rect type, got %s " % type(screen_size_))
        if not PyObject_IsInstance(channels_, int):
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
        cdef int j=0
        self.channels    = [mixer.Channel(j + self.start)
                            for j in range(self.channel_num)]   # create a channel object for controlling playback
        self.snd_obj     = [None] * self.channel_num            # list of un-initialised objects
        self.channel = self.start                               # pointer to the bottom of the stack
        self.all = list(range(self.start, self.end))            # create a list with all channel number
        self.screen_size = screen_size_                         # size of the display (used for stereo mode)


    cpdef void update(self):
        """ 
        THIS METHOD HAS TO BE CALLED FROM THE MAIN LOOP OF YOUR PROGRAM
        DETECT SOUNDS THAT HAVE STOPPED TO PLAY ON THE MIXER AND SET THE CHANNEL VALUE TO NONE
        """
        cdef:
            int i = 0
            snd_obj = self.snd_obj

        for c in self.channels:
            if c:
                # Returns True if the mixer is busy mixing any channels.
                # If the mixer is idle then this return False.
                if not c.get_busy():
                    snd_obj[i] = None
            i += 1

    # SINGLE SOUND
    cpdef void update_sound_panning(self, int new_x_, float volume_, str name_="", object id_=None):

        """
        PANNING IS THE DISTRIBUTION OF A SOUND SIGNAL INTO A NEW STEREO OR MULTI-CHANNEL SOUND FIELD
        CHANGE PANNING FOR ALL SOUNDS BEING PLAYED ON THE MIXER.

        ADJUST THE PANNING OF A GIVEN SOUND (FOUND THE SOUND OBJECT WITH AN EXPLICIT NAME OR ID).
        AT LEAST ONE SEARCH METHOD MUST BE DEFINED.

        :param new_x_  : integer; new sound position in the display. Value must be in range [0, Max width]
        :param volume_ : float; Sound volume (adjust all sound being played by the mixer)
                         value must be in range [0 ... 1.0]
        :param name_   : string; Given sound name (name given at the time eof the SoundObject construction)
        :param id_     : object; Default None. ID number such as object_id_ = id(sound_).
        :return        : None

        """


        assert 0 <= new_x_ <= self.screen_size.w,\
            "\nArgument new_x_ value must be in range (0, %s) got %s" % (self.screen_size.w, new_x_)

        # SET THE VOLUME IN CASE OF AN INPUT ERROR
        if 0.0 >= volume_ >= 1.0:
            volume_ = 1.0

        if name_ == "" and id_ is None:
            raise ValueError("\nInvalid function call, at least one argument must be set!")

        # search by name take precedence (if name value is not undefined)
        if name_ != "":
            id_ = None

        cdef:
            float right, left
            list channels
            int c
            stereo st;

        # Calculate the sound panning, left & right volume values
        st = self.stereo_panning(new_x_, self.screen_size.w)
        left  = st.left
        right = st.right
        left  *= volume_
        right *= volume_

        channels = self.channels  # Fetch all the channels from the sound controller

        for obj in self.snd_obj:  # Iterate all the SoundObject
            if obj:
                if PyObject_HasAttr(obj, "pos") and obj.pos is not None:
                    # search by name
                    if name_ != "":

                        if PyObject_HasAttr(obj, 'name') and hasattr(obj, 'active_channel'):
                            if obj.name == name_:
                                c = obj.active_channel  # Channel playing the sound
                                obj.pos = new_x_        # update the sound position
                                try:
                                    channel = channels[c]
                                    if PyObject_HasAttr(channel, 'set_volume'):
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
                        if PyObject_HasAttr(obj, 'obj_id') and hasattr(obj, 'active_channel'):
                            if obj.obj_id == id_:
                                c = obj.active_channel  # Channel playing the sound
                                obj.pos = new_x_        # update the sound position
                                try:
                                    channel = channels[c]
                                    if PyObject_HasAttr(channel, 'set_volume'):
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
    cpdef void update_sounds_panning(self, int new_x_, float volume_):
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

        cdef:
            float left, right
            list channels
            int c
            stereo st;

        # Calculate the sound panning, left & right volume values
        st    = self.stereo_panning(new_x_, self.screen_size.w)
        left  = st.left
        right = st.right
        left  *= volume_
        right *= volume_

        channels = self.channels    # Fetch all the channels from the sound controller

        for obj in self.snd_obj:    # Iterate all the SoundObject
            if obj:
                if PyObject_HasAttr(obj, "pos") and obj.pos is not None:
                    if PyObject_HasAttr(obj, 'active_channel'):
                        c = obj.active_channel                # Channel playing the sound
                        obj.pos = new_x_                      # update the sound position
                        try:
                            c = channels[c]
                            if PyObject_HasAttr(c, "set_volume"):
                                c.set_volume(left, right)   # set the panning for the channel
                            else:
                                raise AttributeError('\nObject is missing attributes set_volume')
                        except IndexError as e:
                            raise IndexError("\n %s " % e)
                    else:
                        raise AttributeError(
                            "\nSoundObject is missing attribute(s), "
                            "obj must be a SoundObject type got %s " % type(obj))

    cpdef void update_volume(self, float volume_=1.0):
        """
        UPDATE ALL SOUND OBJECT TO A SPECIFIC VOLUME.
        THIS HAS IMMEDIATE EFFECT AND DO NOT FADE THE SOUND  
        
        AFFECT ALL SOUNDS WITH OR WITHOUT PANNING EFFECT.
        PANNING SOUND EFFECT WILL BE CONSERVED AFTER ADJUSTING THE VOLUME    
        
        :param volume_: float; volume value, default is 1.0
        :return       : None 
        """

        # SET THE VOLUME IN CASE OF AN INPUT ERROR
        if 0.0 >= volume_ >= 1.0:
            volume_ = 1.0

        cdef:
            int i = 0
            list objs
            float left, right
            stereo st;

        objs = self.snd_obj

        # SET THE VOLUME FOR ALL SOUNDS
        for channel in self.channels:

            try:
                single_obj = objs[i]
            except IndexError as e:
                raise IndexError("\n %s " % e)

            if single_obj is not None:

                # WITH PANNING
                if PyObject_HasAttr(single_obj, "pos") and single_obj.pos is not None:
                    if PyObject_HasAttr(channel, "set_volume"):
                        # Calculate the sound panning, left & right volume values
                        st = self.stereo_panning(single_obj.pos, self.screen_size.w)
                        left  = st.left
                        right = st.right
                        left  *= volume_
                        right *= volume_
                        channel.set_volume(left, right)

                # WITHOUT PANNING
                else:
                    if single_obj is not None:
                        if PyObject_HasAttr(single_obj.sound, "set_volume"):
                            single_obj.sound.set_volume(volume_)

            i += 1

    cpdef void pause_sound(self, str name_ = "", object id_=None):
        """
        PAUSE A SINGLE SOUND FROM THE MIXER (AT LEAST ONE SEARCH ELEMENT HAS TO BE PROVIDED NAME OR ID)

        :param name_   : string | None; Given sound name (name given at the time eof the SoundObject construction)
        :param id_     : object; Default None. ID number such as object_id_ = id(sound_).
        :return        : None
        """
        if name_ == "" and id_ is None:
            raise ValueError("\nInvalid function call, at least one argument must be set!")

        # search by name take precedence (if name value is not undefined)
        if name_ != "":
            id_ = None
        cdef:
            list objs
            int i

        objs = self.snd_obj
        i = 0
        # SET THE VOLUME FOR ALL SOUNDS
        for channel in self.channels:
            if PyObject_HasAttr(channel, "pause"):
                try:
                    single_obj = objs[i]
                except IndexError as e:
                    raise IndexError("\n %s " % e)

                if single_obj is not None:

                    # search by name
                    if name_ != "":
                        if single_obj.name == name_:
                            channel.pause()

                    # search by id_
                    elif id_ is not None:
                        if single_obj.obj_id == id_:
                            channel.pause()

            i += 1
        ...


    cpdef void pause_sounds(self):
        """
        PAUSE ALL SOUND OBJECTS (THIS HAS IMMEDIATE EFFECT)

        :return       : None
        """
        cdef:
            list objs
            int i = 0

        objs = self.snd_obj

        # SET THE VOLUME FOR ALL SOUNDS
        for channel in self.channels:

            try:
                single_obj = objs[i]
            except IndexError as e:
                raise IndexError("\n %s " % e)

            if single_obj is not None:

                if PyObject_HasAttr(channel, "pause"):
                    channel.pause()
            i += 1

    cpdef void unpause_sounds(self):
        """
        UNPAUSE ALL SOUND OBJECTS (THIS HAS IMMEDIATE EFFECT)

        :return       : None
        """
        cdef:
            list objs
            int i = 0

        objs = self.snd_obj

        for channel in self.channels:

            try:
                single_obj = objs[i]
            except IndexError as e:
                raise IndexError("\n %s " % e)

            if single_obj is not None:
                if PyObject_HasAttr(channel, "unpause"):
                    channel.unpause()
            i += 1

    cpdef void unpause_sound(self, str name_ = "", object id_=None):
        """
        UNPAUSE A SINGLE SOUND FROM THE MIXER (AT LEAST ONE SEARCH ELEMENT HAS TO BE PROVIDED NAME OR ID)

        :param name_   : string | None; Given sound name (name given at the time eof the SoundObject construction)
        :param id_     : object; Default None. ID number such as object_id_ = id(sound_).
        :return        : None
        """

        if name_ == "" and id_ is None:
            raise ValueError("\nInvalid function call, at least one argument must be set!")

        # search by name take precedence (if name value is not undefined)
        if name_ != "":
            id_ = None

        cdef:
            list objs
            int i = 0

        objs = self.snd_obj

        for channel in self.channels:

            try:
                single_obj = objs[i]
            except IndexError as e:
                raise IndexError("\n %s " % e)

            if single_obj is not None:
                # search by name
                if name_ != "":
                    if single_obj.name == name_:
                        channel.unpause()

                # search by id_
                elif id_ is not None:
                    if single_obj.obj_id == id_:
                        channel.unpause()

            i += 1


    cpdef list show_free_channels(self):
        """
        RETURN A LIST OF FREE CHANNELS (NUMERICAL VALUES). 
        :return: list; RETURN A LIST 
        """
        cdef:
            list free_channels = []
            int i = 0
            free_channels_append = free_channels.append
            start = self.start

        for c in self.channels:
            if not c.get_busy():
                free_channels_append(i + start)
            i += 1

        return free_channels

    cpdef void show_sounds_playing(self):
        """
        DISPLAY ALL SOUNDS OBJECTS
        """
        cdef:
            int j = 0
            snd_obj = self.snd_obj
            float timeleft

        for object_ in self.snd_obj:
            if object_:
                timeleft = <float>round(object_.length - (time() - object_.time), 2)
                # if timeleft < 0, most likely to be a sound with attribute loop enabled
                if timeleft < 0.0:
                    timeleft = 0.0

                print('Name %s priority %s  channel %s length(s) %s time left(s) %s' %
                      (object_.name, object_.priority, object_.active_channel,
                       <float>round(object_.length, 2), timeleft))
            j += 1

    cpdef list get_identical_sounds(self, object sound_):
        """ 
        RETURN A LIST OF CHANNEL(S) PLAYING IDENTICAL SOUND OBJECT(s)
        SEARCH BY IDENTICAL PYGAME.SOUND OBJECT
        
        :param sound_: Mixer object; Object to compare to
        :return      : python list; List containing channels number playing similar sound object,
                       if no match is found, return an empty list
        """

        assert isinstance(sound_, pygame.mixer.Sound), \
            "\nPositional argument sound_ must be a pygame.mixer.Sound type, got %s " % type(sound_)

        cdef:
            list duplicate = []
            duplicate_append = duplicate.append

        for obj in self.snd_obj:
            if obj:
                if obj.sound == sound_:
                    duplicate_append(obj.active_channel)
        return duplicate

    cpdef list get_identical_id(self, long long int id_):
        """ 
        RETURN A LIST CONTAINING ANY IDENTICAL SOUND BEING MIXED.
        USE THE UNIQUE ID FOR REFERENCING OBJECTS
        
        :param id_: python integer; unique id number that reference a sound object
        :return: list; Return a list of channels containing identical sound object
        """
        assert isinstance(id_, int), \
            "\nPositional argument id_ must be an int type, got %s " % type(id_)

        cdef:
            list duplicate = []
            duplicate_append = duplicate.append

        for obj in self.snd_obj:
            if obj:
                if obj.obj_id == id_:
                    duplicate_append(obj)
        return duplicate

    cpdef void stop(self, list stop_list_):
        """ 
        STOP ALL SOUND BEING PLAYED ON THE GIVEN LIST OF CHANNELS.
        ONLY SOUND WITH PRIORITY LEVEL 0 CAN BE STOPPED.
        
        :param stop_list_: python list; list of channels
        :return         : None
        """
        assert isinstance(stop_list_, list), \
            "\nPositional argument stop_list must be a python list type, got %s " % type(stop_list_)

        cdef:
            int c, l
            int start = self.start
            snd_obj = self.snd_obj
            channels = self.channels

        for c in stop_list_:
                l = c - start
                if <object>PyList_GetItem(snd_obj, l):
                    if snd_obj[l].priority == 0:
                        channels[l].set_volume(0.0, 0.0)
                        channels[l].stop()
        self.update()

    cpdef void stop_all_except(self, list exception_):
        """ 
        STOP ALL SOUND OBJECT EXCEPT SOUNDS FROM A GIVEN LIST OF ID(SOUND)
        IT WILL STOP SOUND PLAYING ON ALL CHANNELS REGARDLESS
        OF THEIR PRIORITY.
        
        :param exception_: Can be a single pygame.Sound id value or a list containing
                           all pygame.Sound object id numbers.
        """

        assert isinstance(exception_, list),\
            "\nPositional argument exception_ must be a python list type, got %s " % type(exception_)

        cdef:
            int l, c
            int start = self.start
            snd_obj = self.snd_obj
            channels = self.channels

        for c in self.all:
            l = c - start
            snd_object = <object>PyList_GetItem(snd_obj, l)
            if snd_object:
                if snd_object.obj_id not in exception_:
                    channels[l].set_volume(0.0)
                    channels[l].stop()
        self.update()

    cpdef void stop_all(self):
        """
        STOP ALL SOUNDS NO EXCEPTIONS.

        :return: None
        """
        cdef:
            int c, l
            int start = self.start
            snd_obj = self.snd_obj
            channels = self.channels

        for c in self.all:
            l = c - start
            snd_object = <object>PyList_GetItem(snd_obj, l)
            if snd_object:
                channels[l].set_volume(0.0)
                channels[l].stop()
        self.update()

    cpdef void stop_name(self, str name_=""):
        """
        STOP A PYGAME.SOUND OBJECT IF PLAYING ON ANY OF THE CHANNELS.
        :param name_: string; Sound name to stop
        :return     :  None
        """
        assert isinstance(name_, str),\
            "\nPositional argument name_ must be a python string type, got %s " % type(name_)
        cdef:
            channels = self.channels
            int start = self.start

        for sound in self.snd_obj:
            if sound and sound.name == name_:
                try:
                    channels[sound.active_channel - start].set_volume(0.0)
                    channels[sound.active_channel - start].stop()
                except IndexError:
                    # IGNORE ERROR
                    ...
        self.update()

    cpdef void stop_object(self, long long int object_id):
        """
        STOP A GIVEN SOUND USING THE PYGAME.SOUND OBJECT ID NUMBER.

        :param object_id: integer; Object unique identifier such as id(sound)
        :return         : None
        """
        assert isinstance(object_id, int), \
            "\nPositional argument object_id must be a python string type, got %s " % type(object_id)
        cdef:
            channels = self.channels
            int start = self.start

        for sound in self.snd_obj:
            if sound and sound.obj_id == object_id:
                try:
                    channels[sound.active_channel - start].set_volume(0.0)
                    channels[sound.active_channel - start].stop()
                except IndexError:
                    # IGNORE ERROR
                    ...

        self.update()

    cpdef float return_time_left(self, long long int object_id):
        """
        RETURN THE TIME LEFT IN SECONDS (RETURN -1 IF SOUND IS SEAMLESS LOOPED ON THE CHANNEL,
        AND NONE WHEN SOUND IS NOT FOUND

        :param object_id: python integer; unique object id
        :return         : float | None; Return a float representing the time left in seconds.
        """
        cdef:
            int j = 0
            snd_obj = self.snd_obj
            float timeleft

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
        return 0.0

    cpdef int get_reserved_channels(self):
        """ RETURN THE NUMBER OF RESERVED CHANNELS """
        return self.channel_num

    cpdef int get_reserved_start(self):
        """ RETURN THE FIRST RESERVED CHANNEL NUMBER """
        return self.start

    cpdef int get_reserved_end(self):
        """ RETURN THE LAST RESERVED CHANNEL NUMBER """
        return self.end

    cpdef list get_channels(self):
        """ 
        RETURN A LIST OF ALL RESERVED PYGAME MIXER CHANNELS.
        """
        return self.channels

    cpdef get_sound(self, int channel_):
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

    cpdef get_sound_object(self, int channel_):
        """ 
        RETURN A SPECIFIC SOUND OBJECT 
        RETURN NONE IN CASE OF AN INDEX ERROR
        """
        try:
            s = <object>PyList_GetItem(self.snd_obj, channel_)
        except IndexError:
            return None
        else:
            return s

    cpdef list get_all_sound_object(self):
        """ RETURN ALL SOUND OBJECTS """
        return self.snd_obj

    cpdef play(self, sound_, int loop_, int priority_=0, float volume_=1.0,
               float fade_in_ms=100.0, float fade_out_ms=100.0, bint panning_=False, name_=None,
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

        cdef:
            int l = 0
            list channels = self.channels
            int channel  = self.channel
            int start    = self.start
            int end      = self.end
            int screen_width = self.screen_size.w
            stereo st;

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
                    st = self.stereo_panning(x_, self.screen_size.w)
                    channels[l].set_volume(st.left * volume_, st.right * volume_)

                else:
                    channels[l].set_volume(volume_)

                channels[l].fadeout(<int>fade_out_ms)
                channels[l].play(sound_, loops=loop_, maxtime=0, fade_ms=<int>fade_out_ms)

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

    cpdef void display_size_update(self, rect_):
        """
        UPDATE THE SCREEN SIZE AFTER CHANGING MODE
        THIS FUNCTION IS MAINLY USED FOR THE PANNING MODE (STEREO) 
        :param rect_: pygame.Rect; display dimension 
        :return: None
        """
        self.screen_size = rect_

    cdef inline stereo stereo_panning(self, int x_, int screen_width)nogil:
        """
        STEREO MODE 
        
        :param screen_width: display width 
        :param x_          : integer; x value of sprite position on screen  
        :return: tuple of float; 
        """
        cdef:
            float right_volume=0.0, left_volume=0.0
        cdef stereo st;
        st.left  = 0;
        st.right = 0;

        # MUTE THE SOUND IF OUTSIDE THE BOUNDARIES
        if 0 > x_ > screen_width:
            return st

        right_volume = float(x_) / <float>screen_width
        left_volume =  1.0 - right_volume

        st.left  = left_volume
        st.right = right_volume
        return st
