#!/usr/bin/env python
# -*- coding:utf-8 -*-
import fractions
import re

FPS_NTSC_FILM = fractions.Fraction(24000, 1001)
FPS_NTSC = fractions.Fraction(30000, 1001)
FPS_NTSC_DOUBLE = fractions.Fraction(60000, 1001)
FPS_NTSC_QUAD = fractions.Fraction(120000, 1001)
FPS_FILM = 24
FPS_PAL = 25
FPS_PAL_DOUBLE = 50
FPS_PAL_QUAD = 100

RE_STRTIME = re.compile("(\d):(\d+):(\d+).(\d+)")


def ms_to_strtime(timems):
    """Convert Milliseconds to ASS string time"""
    s, ms = divmod(timems, 1000)
    m, s = divmod(s, 60)
    h, m = divmod(m, 60)
    cs, ms = divmod(ms, 10)
    return "{:01d}:{:02d}:{:02d}.{:02d}".format(h, m, s, cs)


def ms_to_cs(ms):
    """Convert Millisecons to Centiseconds"""
    return ms / 10


def ms_to_s(ms):
    """Convert Milliseconds to Seconds"""
    return ms / 1000


def ms_to_frames(ms, framerate=FPS_NTSC_FILM):
    """Convert Frames to Milliseconds"""
    return int(math.floor(framerate * ms_to_s(ms)))


def cs_to_ms(cs):
    """Convert Centisecods to Milliseconds"""
    return cs * 10


def cs_to_s(cs):
    """Convert Centiseconds to Secons"""
    return cs_to_ms(cs) / 1000


def cs_to_strtime(cs):
    """Convert Centisecons to ass string time"""
    return ms_to_strtime(cs_to_ms(cs))


def cs_to_frames(cs, framerate=FPS_NTSC_FILM):
    """Convert Centiseconds to Frames"""
    return ms_to_frames(cs_to_ms(cs), framerate)


def s_to_ms(s):
    """Convert Seconds to Millisecons"""
    return s * 1000


def s_to_cs(s):
    """Convert Seconds to Centiseconds"""
    return ms_to_cs(s_to_ms(s))


def s_to_strtime(s):
    """Convert Seconds to ASS string time"""
    return ms_to_strtime(s_to_ms(s))


def s_to_frames(s, framerate=FPS_NTSC_FILM):
    """Convert Seconds to Frames"""
    return ms_to_frames(s_to_ms(s), framerate)


def frames_to_s(frames, framerate=FPS_NTSC_FILM):
    """Convert Frames to Seconds"""
    return frames / framerate


def frames_to_ms(frames, framerate):
    """Convert Frames to Milliseconds"""
    return s_to_ms(frames_to_s(frames, framerate))


def frames_to_cs(frames, framerate):
    """Convert Frames to centiceconds"""
    return s_to_cs(frames_to_s(frames, framerate))


def frames_to_strtime(frames, framerate):
    """Convert Frames to ASS string time"""
    return s_to_strtime(frames_to_s(frames, framerate))


def strtime_to_ms(time):
    """Convert ASS string time to Milliseconds"""
    # H:MM:SS.CC (H=Hour, M=Minute, S=Second, C=centisecond)
    return struct_to_ms(*strtime_to_struct(time))


def strtime_to_struct(time):
    return map(int, re.match(RE_STRTIME, time).groups())


def struct_to_ms(h, m, s, cs):
    return (h * 3600 + m * 60 + s) * 1000 + cs * 10


def strtime_to_cs(time):
    """Convert ASS string time to Centiseconds"""
    return ms_to_cs(strtime_to_ms(time))


def strtime_to_s(time):
    """Convert ASS string time to Seconds"""
    return ms_to_s(strtime_to_ms(time))


def strtime_to_frames(time):
    """Convert ASS string time to Frames"""
    return ms_to_frames(strtime_to_ms(time))


class Time(object):

    """Time Object"""

    def __init__(self, time=None):
        if time:
            self.ms = int(round(time))
        else:
            self.ms = 0

    @property
    def cs(self):
        """Get time in centiseconds"""
        return ms_to_cs(self.ms)

    @property
    def s(self):
        """Get time in seconds"""
        return ms_to_s(self.ms)

    def frames(self, framerate=FPS_NTSC_FILM):
        """Get time in number of frames"""
        return ms_to_frames(self.ms, framerate)

    @property
    def strtime(self):
        """Get time in ASS string time"""
        return ms_to_strtime(self.ms)

    @classmethod
    def from_cs(cls, cs):
        """Create new `Time` from centiseconds"""
        return cls(cs_to_ms(cs))

    @classmethod
    def from_s(cls, s):
        """Create new `Time` from seconds

        @s: seconds
        """
        return cls(s_to_ms(s))

    @classmethod
    def from_frame(cls, frame, framerate=FPS_NTSC_FILM):
        """Create new `Time` from frames

        @frames: frames
        @framerate: framerate
        """
        return cls(frames_to_ms(frame, framerate))

    @classmethod
    def from_strtime(cls, time):
        """Create new `Time` from ASS time string

        @time: sting time.
        H:MM:SS.CC (H=Hour, M=Minute, S=Second, C=centisecond)
        """
        return cls(strtime_to_ms(time))

    def __sub__(self, other):
        """Substraction of times"""
        if isinstance(other, int):
            return Time(self.ms - other)
        elif isinstance(other, float):
            return Time(self.ms - other)
        else:
            return Time(self.ms - other.ms)

    __rsub__ = __sub__

    def __div__(self, other):
        """Divition of times"""
        if isinstance(other, int):
            return Time(self.ms / other)
        elif isinstance(other, float):
            return Time(self.ms / other)
        else:
            return Time(self.ms / other.ms)

    __rdiv__ = __div__

    def __truediv__(self, other):
        """Divition of times"""
        if isinstance(other, int):
            return Time(self.ms / float(other))
        elif isinstance(other, float):
            return Time(self.ms / other)
        else:
            return Time(self.ms / other.ms)

    __rtruediv__ = __truediv__

    def __add__(self, other):
        """Addition of times"""
        if isinstance(other, int):
            return Time(self.ms + other)
        elif isinstance(other, float):
            return Time(self.ms + other)
        else:
            return Time(self.ms + other.ms)

    __radd__ = __add__

    def __mul__(self, other):
        """Multiplication of times"""
        if isinstance(other, int):
            return Time(self.ms * other)
        elif isinstance(other, float):
            return Time(self.ms * other)
        else:
            return Time(self.ms * other.ms)

    __rmul__ = __mul__

    def __ne__(self, other):
        return not self.__eq__(other)

    def __eq__(self, other):
        if isinstance(other, Time):
            return self.ms == other.ms
        else:
            return self.ms == other

    def __cmp__(self, other):
        t1 = self.ms
        if isinstance(other, Time):
            t2 = other.ms
        else:
            t2 = other
        if t1 == t2:
            return 0
        elif t1 > t2:
            return 1
        elif t1 < t2:
            return -1

    def __lt__(self, other):
        t1 = self.ms
        if isinstance(other, Time):
            t2 = other.ms
        else:
            t2 = other
        return t1 < t2

    def __le__(self, other):
        t1 = self.ms
        if isinstance(other, Time):
            t2 = other.ms
        else:
            t2 = other
        return t1 <= t2

    def __gt__(self, other):
        t1 = self.ms
        if isinstance(other, Time):
            t2 = other.ms
        else:
            t2 = other
        return t1 > t2

    def __ge__(self, other):
        t1 = self.ms
        if isinstance(other, Time):
            t2 = other.ms
        else:
            t2 = other
        return t1 >= t2

    def __str__(self):
        return "<Time " + self.strtime + " >"

    def __repr__(self):
        return repr("<Time " + self.strtime + " >")
