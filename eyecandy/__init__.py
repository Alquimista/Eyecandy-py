#!/usr/bin/env python
# -*- coding:utf-8 -*-

try:
    from asstime import (
        FPS_FILM,
        FPS_NTSC,
        FPS_NTSC_DOUBLE,
        FPS_NTSC_FILM,
        FPS_NTSC_QUAD,
        FPS_PAL,
        FPS_PAL_DOUBLE,
        FPS_PAL_QUAD,
        Time,
    )
    from color import Color
    from effector import Generator as load
    from helpers import timeit
    from interpolate import DEFAULT_INTERPOLATE
    from reader import VIDEO_ZOOM
except ImportError:
    from .asstime import (
        FPS_FILM,
        FPS_NTSC,
        FPS_NTSC_DOUBLE,
        FPS_NTSC_FILM,
        FPS_NTSC_QUAD,
        FPS_PAL,
        FPS_PAL_DOUBLE,
        FPS_PAL_QUAD,
        Time,
    )
    from .color import Color
    from .effector import Generator as load
    from .helpers import timeit
    from .interpolate import DEFAULT_INTERPOLATE
    from .reader import VIDEO_ZOOM

ALIGN = {
    "top left": 7,
    "top center": 8,
    "top right": 9,
    "middle left": 4,
    "middle center": 5,
    "middle right": 6,
    "bottom left": 1,
    "bottom center": 2,
    "bottom right": 3,
}
