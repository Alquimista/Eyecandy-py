#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division

import random

import eyecandy
from eyecandy import interpolate, color
from eyecandy.asstags import *

if __name__ == '__main__':

    bord = 10
    width = 100
    height = None

    shape = shape_square(width)
    maxx, maxy = shape_max(shape)
    square1 = translate_shape(shape, -maxx / 2, -maxy / 2)

    shape_p = shape_square(width - bord * 2)
    maxx2, maxy2 = shape_max(shape_p)
    square2 = translate_shape(shape_p, -maxx2 / 2, -maxy2 / 2)
    square2 = flip_shape(square2)

    squares = square1 + square2
    maxx3, maxy3 = shape_max(squares)
    squares = translate_shape(square1 + square2, maxx3, maxy3)

    print(square1)
    print(square2)

    print(p(1, squares))
