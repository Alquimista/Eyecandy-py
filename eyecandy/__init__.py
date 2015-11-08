#!/usr/bin/env python
#-*- coding:utf-8 -*-

try:
    from effector import Generator as load
    from helpers import timeit
    from asstime import (Time, FPS_NTSC_FILM, FPS_NTSC, FPS_NTSC_DOUBLE,
                         FPS_NTSC_QUAD, FPS_FILM, FPS_PAL, FPS_PAL_DOUBLE,
                         FPS_PAL_QUAD)
    from color import Color
    from interpolate import DEFAULT_INTERPOLATE
    from reader import VIDEO_ZOOM
except ImportError:
    from .effector import Generator as load
    from .helpers import timeit
    from .asstime import (Time, FPS_NTSC_FILM, FPS_NTSC, FPS_NTSC_DOUBLE,
                          FPS_NTSC_QUAD, FPS_FILM, FPS_PAL, FPS_PAL_DOUBLE,
                          FPS_PAL_QUAD)
    from .color import Color
    from .interpolate import DEFAULT_INTERPOLATE
    from .reader import VIDEO_ZOOM

ALIGN = {
    'top left': 7, 'top center': 8, 'top right': 9,
    'middle left': 4, 'middle center': 5, 'middle right': 6,
    'bottom left': 1, 'bottom center': 2, 'bottom right': 3}
