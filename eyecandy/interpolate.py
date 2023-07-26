#!/usr/bin/env python2
# -*- coding:utf-8 -*-
from __future__ import absolute_import, division, print_function, with_statement

import math

""""
Simple interpolation
"""

# Equations
# http://codeplea.com/simple-interpolation
# http://algorithmist.wordpress.com/

_fact_cache = {}


def fact(n):
    """Memoized factorial function"""
    try:
        return _fact_cache[n]
    except KeyError:
        if n == 1 or n == 0:
            result = 1
        else:
            result = n * fact(n - 1)
        _fact_cache[n] = result
        return result


# fact = math.factorial


# NyuFx
# Binomial coefficient
def binomial(i, n):
    return fact(n) / (fact(i) * fact(n - i))


# Bernstein polynom
def bernstein(t, i, n):
    return binomial(i, n) * pow(t, i) * pow((1 - t), n - i)


def bezier_curve(t, p):
    """Bezier Curve"""
    # Calculate coordinate
    n = len(p) - 1
    num = 0
    for i, position in enumerate(p):
        num += position * bernstein(t, i, n)
    return num


# Interpolate funcs
def linear(t, start, end):
    return t * (end - start) + start


# For gradient Color correction
# https://youtu.be/LKnqECcg6Gw
def linear_squared(t, start, end):
    return math.sqrt(linear(t, start**2, end**2))


def cosine(t, start, end, repeat=None):
    if not repeat:
        repeat = 1
    t = 0.5 - (math.cos(repeat * math.pi * t) / 2)
    return linear(t, start, end)


def sine(t, start, end):
    t = math.sin((math.pi * t) / 2)
    return linear(t, start, end)


def smooth_step(t, start, end):
    t = (t**2) * (3 - (2 * t))
    return linear(t, start, end)


def smooth_step_double(t, start, end):
    t = smooth_step(t, start, end)
    return smooth_step(t, start, end)


def acceleration(t, start, end):
    t **= 2
    return linear(t, start, end)


def cubic_acceleration(t, start, end):
    t **= 3
    return linear(t, start, end)


def deccelaration(t, start, end):
    t = 1 - (1 - t) ** 2
    return linear(t, start, end)


def cubic_deccelaration(t, start, end):
    t = 1 - (1 - t) ** 3
    return linear(t, start, end)


def sigmoid(t, start, end):
    t = 1 / (1 + math.exp(-t))
    return linear(t, start, end)


# http://cubic-bezier.com


def custom_curve(t, curve, start, end):
    t = bezier_curve(t, curve)
    return linear(t, start, end)


# http://matthewlein.com/ceaser/
def ease(t, start, end):
    return custom_curve(t, (0.25, 0.1, 0.25, 1), start, end)


def ease_in(t, start, end):
    return custom_curve(t, (0.42, 0, 1, 1), start, end)


def ease_out(t, start, end):
    return custom_curve(t, (0, 0, 0.58, 1), start, end)


def ease_in_out(t, start, end):
    return custom_curve(t, (0.420, 0.000, 0.580, 1.000), start, end)


# Penner Equation (aproximated)
def ease_in_quad(t, start, end):
    return custom_curve(t, (0.550, 0.085, 0.680, 0.530), start, end)


def ease_in_cubic(t, start, end):
    return custom_curve(t, (0.550, 0.055, 0.675, 0.190), start, end)


def ease_in_quart(t, start, end):
    return custom_curve(t, (0.895, 0.030, 0.685, 0.220), start, end)


def ease_in_quint(t, start, end):
    return custom_curve(t, (0.755, 0.050, 0.855, 0.060), start, end)


def ease_in_sine(t, start, end):
    return custom_curve(t, (0.470, 0.000, 0.745, 0.715), start, end)


def ease_in_expo(t, start, end):
    return custom_curve(t, (0.950, 0.050, 0.795, 0.035), start, end)


def ease_in_circ(t, start, end):
    return custom_curve(t, (0.600, 0.040, 0.980, 0.335), start, end)


def ease_out_quad(t, start, end):
    return custom_curve(t, (0.250, 0.460, 0.450, 0.940), start, end)


def ease_out_cubic(t, start, end):
    return custom_curve(t, (0.215, 0.610, 0.355, 1.000), start, end)


def ease_out_quart(t, start, end):
    return custom_curve(t, (0.165, 0.840, 0.440, 1.000), start, end)


def ease_out_quint(t, start, end):
    return custom_curve(t, (0.230, 1.000, 0.320, 1.000), start, end)


def ease_out_sine(t, start, end):
    return custom_curve(t, (0.390, 0.575, 0.565, 1.000), start, end)


def ease_out_expo(t, start, end):
    return custom_curve(t, (0.190, 1.000, 0.220, 1.000), start, end)


def ease_out_circ(t, start, end):
    return custom_curve(t, (0.075, 0.820, 0.165, 1.000), start, end)


def ease_in_out_quad(t, start, end):
    return custom_curve(t, (0.455, 0.030, 0.515, 0.955), start, end)


def ease_in_out_cubic(t, start, end):
    return custom_curve(t, (0.645, 0.045, 0.355, 1.000), start, end)


def ease_in_out_quart(t, start, end):
    return custom_curve(t, (0.770, 0.000, 0.175, 1.000), start, end)


def ease_in_out_quint(t, start, end):
    return custom_curve(t, (0.860, 0.000, 0.070, 1.000), start, end)


def ease_in_out_sine(t, start, end):
    return custom_curve(t, (0.445, 0.050, 0.550, 0.950), start, end)


def ease_in_out_expo(t, start, end):
    return custom_curve(t, (1.000, 0.000, 0.000, 1.000), start, end)


def ease_in_out_circ(t, start, end):
    return custom_curve(t, (0.785, 0.135, 0.150, 0.860), start, end)


# KAFX Equations
def backstart(t, start, end):
    return custom_curve(t, (0, 0, 0.2, -0.3, 0.6, 0.26, 1, 1), start, end)


def boing(t, start, end):
    return custom_curve(t, (0, 0, 0.42, 0.0, 0.58, 1.5, 1, 1), start, end)


def interpolate_range(start, end, steps, func=linear, repeat=None):
    nsteps = steps - 1
    for i in range(steps):
        t = i / nsteps
        if repeat:
            yield func(t, start, end, repeat)
        else:
            yield func(t, start, end)


def interpolate_circle_range(steps, func=linear):
    return list(interpolate_range(0, 360, steps + 1, func))[:steps]


def bezier_curve_range(steps, points):
    """Range of points in a curve bezier"""
    points = list(zip(*points))
    for i in range(steps):
        t = i / float(steps - 1)
        yield [bezier_curve(t, points[i]) for i in range(len(points))]


DEFAULT_INTERPOLATE = linear

if __name__ == "__main__":
    # print(
    #     list(interpolate_range(
    #         start=0, end=10, steps=20, func=cosine, repeat=8)))
    # print(list(interpolate_range(start=0, end=10, steps=20, func=sine)))
    vueltas = 3
    n = 10
    print(
        list(
            int(round(math.degrees(radian), 0))
            for radian in interpolate_range(0, vueltas * 2 * math.pi, n + 1)
        )
    )
