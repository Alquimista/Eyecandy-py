#!/usr/bin/env python
#-*- coding:utf-8 -*-
from __future__ import (absolute_import, division,
                        with_statement, print_function)

import colorsys
import math
import random
import re

import string
import sys

try:
    import interpolate
except ImportError:
    from . import interpolate

_HEXVALUES = "0123456789ABCDEF"
try:
    _TABLE_INVERT_COLOR = string.maketrans(_HEXVALUES, _HEXVALUES[::-1])
except AttributeError:
    _TABLE_INVERT_COLOR = str.maketrans(_HEXVALUES, _HEXVALUES[::-1])
DEFAULT_INTERPOLATE = interpolate.linear_squared
_HEX_COLOR_RE = re.compile(r'^(?:\A#)*([a-fA-F0-9]{3}\Z|[a-fA-F0-9]{6})$\Z')
_ASS_COLOR_RE = re.compile('&H(?:[a-fA-F0-9]{2})*([a-fA-F0-9]{6})')


def rainbow(n=6, s=100, v=100, func=interpolate.linear):
    for hue in interpolate.interpolate_circle_range(n, func):
        yield Color.from_hsv(hue, s, v)


def validate_range_values(values, range=(0, 255),
                          error='tuple values must be from 0-255.'):
    """Validate the range of the color components."""
    for value in values:
        if range[0] < value > range[1]:
            raise ValueError(error)


def _gradient(color1, color2, steps, func=DEFAULT_INTERPOLATE):
    irange = interpolate.interpolate_range
    rgbcolors = (
        irange(color1[i], color2[i], steps, func) for i in range(3))
    for r, g, b in zip(*rgbcolors):
        yield Color(r, g, b)


def gradient(colors, steps, func=DEFAULT_INTERPOLATE):
    if len(colors) > steps:
        raise ValueError(
            "The number of colors can not be greater than the steps")
    if steps == len(colors):
        for color in colors:
            yield color
    else:
        num_out = int(steps / (len(colors) - 1))
        gradient_color = _gradient(colors[0], colors[1], num_out, func)
        if len(colors) > 2:
            for i in range(len(colors) - 1):
                if i == len(colors) - 2 and steps % 2 == 1:
                    num_out += 1
                for color in _gradient(
                        colors[i],
                        colors[i + 1],
                        num_out,
                        func):
                    yield color
        else:
            for color in gradient_color:
                yield color


def gradient_bezier(colors, steps):
    if len(colors) > steps:
        raise ValueError(
            "The number of colors can not be greater than the steps")
    if steps == len(colors):
        for color in colors:
            yield color
    else:
        for r, g, b in interpolate.bezier_curve_range(steps, colors):
            yield Color(r, g, b)


class BaseColor(object):

    def __init__(self, c1=None, c2=None, c3=None):
        super(BaseColor, self).__init__()

        if c1 != None and c2 == None and c3 == None:
            c2 = c1
            c3 = c1

        c1 = 0 if not c1 else c1
        c2 = 0 if not c2 else c2
        c3 = 0 if not c3 else c3

        if (self._valid_range_min <= int(c1) < self._valid_range_max + 1 and
                self._valid_range_min <= int(c2) < self._valid_range_max + 1 and
                self._valid_range_min <= int(c3) < self._valid_range_max + 1):
            self._color = [int(c1), int(c2), int(c3)]
        else:
            raise ValueError("Color values out of range [{:d}, {:d}]".format(
                self._valid_range_min, self._valid_range_max))

    def _get_component1(self):
        return self._color[0]

    def _get_component2(self):
        return self._color[1]

    def _get_component3(self):
        return self._color[2]

    def _set_component(self, index, value):
        if self._valid_range_min <= value < self._valid_range_max:
            self._color[index] = int(value)
        else:
            error_msg = 'Color value {:d} out of range [{:d}, {:d}]'.format(
                value, self._valid_range_min, self._valid_range_max)
            raise ValueError(error_msg)

    def _set_component1(self, value):
        return self._set_component(0, value)

    def _set_component2(self, value):
        return self._set_component(1, value)

    def _set_component3(self, value):
        return self._set_component(2, value)

    def __contains__(self, item):
        return item in self.rgb

    def __add__(self, other):
        """Mix RGB colors

        Example:
        >>> red = Color(255, 0, 0)
        >>> blue = Color(0, 0, 255)
        >>> purple = red + blue
        >>> purple.rgb
        (128, 0, 128)
        """
        r = math.ceil((self._red + other._red) / 2)
        g = math.ceil((self._green + other._green) / 2)
        b = math.ceil((self._blue + other._blue) / 2)
        return Color(r, g, b)

    def __getitem__(self, key):
        return self._color[key]

    def __setitem__(self, key, value):
        if not self._valid_range_min <= value < self._valid_range_max:
            error_msg = 'Color value {:d} out of range [{:d}, {:d}]'.format(
                value, self._valid_range_min, self._valid_range_max)
            raise ValueError(error_msg)
        self._color[key] = value

    def __len__(self):
        return 3

    def __iter__(self):
        return iter(self._color)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __eq__(self, other):
        if isinstance(other, BaseColor):
            return self._color == other._color

    def __str__(self):
        return ", ".join(map(str, self._color))

    if sys.version_info[0] < 3:
        def __unicode__(self):
            return unicode(", ".join(map(str, self._color)))

    def __repr__(self):
        return "<{} {}, {}, {}>".format(self.__class__.__name__, *self._color)


class Color(BaseColor):

    def __init__(self, r=None, g=None, b=None):
        self._valid_range_max = 255
        self._valid_range_min = 0

        super(Color, self).__init__(r, g, b)

    # get/set values
    @property
    def r(self):
        return self._get_component1()

    @property
    def g(self):
        return self._get_component2()

    @property
    def b(self):
        return self._get_component3()

    @r.setter
    def r(self, value):
        return self._set_component1(value)

    @g.setter
    def g(self, value):
        return self._set_component2(value)

    @b.setter
    def b(self, value):
        return self._set_component3(value)

    @property
    def rgb(self):
        return self.r, self.g, self.b

    @classmethod
    def from_hsv(cls, h, s, v):
        validate_range_values(
            values=(h, 0), range=(0, 360),
            error="H value must be from 0-360.")
        validate_range_values(
            values=(s, v), range=(0, 100),
            error="S and V values must be from 0-100.")
        rgb = colorsys.hsv_to_rgb(h / 360, s / 100, v / 100)
        return cls(*(value * 255 for value in rgb))

    @property
    def hsv(self):
        h, s, v = colorsys.rgb_to_hsv(*(c / 255 for c in self.rgb))
        return h * 360, s * 100, v * 100

    @classmethod
    def from_hls(cls, h, l, s):
        validate_range_values(
            values=(h, 0), range=(0, 360),
            error="H value must be from 0-360.")
        validate_range_values(
            values=(s, l), range=(0, 100),
            error="L and S values must be from 0-100.")
        rgb = colorsys.hls_to_rgb(h / 360, l / 100, s / 100)
        return cls(*(value * 255 for value in rgb))

    @property
    def hls(self):
        h, l, s = colorsys.rgb_to_hls(*(c / 255 for c in self.rgb))
        return h * 360, l * 100, s * 100

    @classmethod
    def from_hex(cls, hexstring):
        """Create new `Color` object from hex representation.

        Example:
        >>>
        <Color 255, 0, 255>
        """
        try:
            hexstring = _HEX_COLOR_RE.match(hexstring).group(1)
        except AttributeError:
            raise ValueError("'{}' is not a valid hexadecimal"
                             "color value.".format(hexstring))
        if len(hexstring) == 3:
            components = [(2 * s) for s in hexstring]
        else:
            components = hexstring[0:2], hexstring[2:4], hexstring[4:6]
        return cls(*(int(s, 16) for s in components))

    @property
    def hex(self):
        return "#{:02X}{:02X}{:02X}".format(*self.rgb)

    @classmethod
    def from_bgrhex(cls, hexstring):
        try:
            hexstring = _HEX_COLOR_RE.match(hexstring).group(1)
        except AttributeError:
            raise ValueError("'{}' is not a valid hexadecimal"
                             "color value.".format(hexstring))
        if len(hexstring) == 3:
            components = [(2 * s) for s in hexstring]
        else:
            components = hexstring[0:2], hexstring[2:4], hexstring[4:6]
        return cls(*(int(s, 16) for s in components[::-1]))

    @classmethod
    def from_ass(cls, color):
        m = re.search(_ASS_COLOR_RE, color)
        hexstring = m.group(1)
        return cls.from_bgrhex(hexstring)

    @property
    def ass(self):
        return "&H{:02X}{:02X}{:02X}&".format(*self.rgb[::-1])

    @property
    def ass_long(self):
        return ("&H00{:02X}{:02X}{:02X}&").format(*self.rgb[::-1])

    @classmethod
    def from_random(cls):
        """Retorna un Color Aleatorio."""
        return cls.from_hex("".join(random.sample(_HEXVALUES,  6)))

    def complementary(self):
        hue, saturation, value = self.hsv
        hue = (hue + 180) % 360
        return Color.from_hsv(hue, saturation, value)

    def analog(self, ncolors=3, separation=10):
        hue, saturation, value = self.hsv
        ncolors += 1
        colors = []
        sep = separation
        signo = -1
        for i in range(1, ncolors):
            hue = (hue + sep * signo) % 360
            if signo < 0:
                colors.insert(0, Color.from_hsv(hue, saturation, value))
            else:
                colors.append(Color.from_hsv(hue, saturation, value))
            if i % 2:
                sep += separation
            signo *= -1
        return colors

    def lighter(self, amt=20):
        """Return a lighter version of this color."""
        h, s, l = self.hls
        l = min(l + amt, 100)
        return Color.from_hls(h, l, s)

    def darker(self, amt=20):
        """Return a darker version of this color."""
        h, s, l = self.hls
        l = min(l - amt, 100)
        return Color.from_hls(h, l, s)

    def grayscale(self):
        """Desaturate the color."""
        luma = 0.3 * self.r + 0.59 * self.g + 0.11 * self.b
        return Color(luma, luma, luma)

    def tinted(self, other, bias=0.5):
        '''
        Return a new color, interpolated between this color and `other` by an
        amount specified by `bias`, which normally ranges from 0 (entirely
        this color) to 1.0 (entirely `other`.)
        '''
        unbias = 1.0 - bias
        return Color(
            self.r * unbias + other.r * bias,
            self.g * unbias + other.g * bias,
            self.b * unbias + other.b * bias,
        )

    greyscale = grayscale

    def gradient(self, target, steps, func=DEFAULT_INTERPOLATE):
        """Generate a range of color from start to end (inclusive).

        Example:
        >>> c1 = Color(255, 255, 255)
        >>> c2 = Color(0, 0, 0)
        >>> c1.gradient(c2, 3)
        [<Color 255, 255, 255>, <Color 127, 127, 127>, <Color 0, 0, 0>]
        """
        for color in _gradient(self, target, steps, func):
            yield color

    def invert(self):
        return self.from_hex(self.hex.translate(_TABLE_INVERT_COLOR))


aliceblue = Color.from_hex('#f0f8ff')
antiquewhite = Color.from_hex('#faebd7')
aqua = Color.from_hex('#00ffff')
aquamarine = Color.from_hex('#7fffd4')
azure = Color.from_hex('#f0ffff')
beige = Color.from_hex('#f5f5dc')
bisque = Color.from_hex('#ffe4c4')
black = Color.from_hex('#000000')
blanchedalmond = Color.from_hex('#ffebcd')
blue = Color.from_hex('#0000ff')
blueviolet = Color.from_hex('#8a2be2')
brown = Color.from_hex('#a52a2a')
burlywood = Color.from_hex('#deb887')
cadetblue = Color.from_hex('#5f9ea0')
chartreuse = Color.from_hex('#7fff00')
chocolate = Color.from_hex('#d2691e')
coral = Color.from_hex('#ff7f50')
cornflowerblue = Color.from_hex('#6495ed')
cornsilk = Color.from_hex('#fff8dc')
crimson = Color.from_hex('#dc143c')
cyan = Color.from_hex('#00ffff')
darkblue = Color.from_hex('#00008b')
darkcyan = Color.from_hex('#008b8b')
darkgoldenrod = Color.from_hex('#b8860b')
darkgray = Color.from_hex('#a9a9a9')
darkgrey = Color.from_hex('#a9a9a9')
darkgreen = Color.from_hex('#006400')
darkkhaki = Color.from_hex('#bdb76b')
darkmagenta = Color.from_hex('#8b008b')
darkolivegreen = Color.from_hex('#556b2f')
darkorange = Color.from_hex('#ff8c00')
darkorchid = Color.from_hex('#9932cc')
darkred = Color.from_hex('#8b0000')
darksalmon = Color.from_hex('#e9967a')
darkseagreen = Color.from_hex('#8fbc8f')
darkslateblue = Color.from_hex('#483d8b')
darkslategray = Color.from_hex('#2f4f4f')
darkslategrey = Color.from_hex('#2f4f4f')
darkturquoise = Color.from_hex('#00ced1')
darkviolet = Color.from_hex('#9400d3')
deeppink = Color.from_hex('#ff1493')
deepskyblue = Color.from_hex('#00bfff')
dimgray = Color.from_hex('#696969')
dimgrey = Color.from_hex('#696969')
dodgerblue = Color.from_hex('#1e90ff')
firebrick = Color.from_hex('#b22222')
floralwhite = Color.from_hex('#fffaf0')
forestgreen = Color.from_hex('#228b22')
fuchsia = Color.from_hex('#ff00ff')
gainsboro = Color.from_hex('#dcdcdc')
ghostwhite = Color.from_hex('#f8f8ff')
gold = Color.from_hex('#ffd700')
goldenrod = Color.from_hex('#daa520')
gray = Color.from_hex('#808080')
grey = Color.from_hex('#808080')
green = Color.from_hex('#008000')
greenyellow = Color.from_hex('#adff2f')
honeydew = Color.from_hex('#f0fff0')
hotpink = Color.from_hex('#ff69b4')
indianred = Color.from_hex('#cd5c5c')
indigo = Color.from_hex('#4b0082')
ivory = Color.from_hex('#fffff0')
khaki = Color.from_hex('#f0e68c')
lavender = Color.from_hex('#e6e6fa')
lavenderblush = Color.from_hex('#fff0f5')
lawngreen = Color.from_hex('#7cfc00')
lemonchiffon = Color.from_hex('#fffacd')
lightblue = Color.from_hex('#add8e6')
lightcoral = Color.from_hex('#f08080')
lightcyan = Color.from_hex('#e0ffff')
lightgoldenrodyellow = Color.from_hex('#fafad2')
lightgray = Color.from_hex('#d3d3d3')
lightgrey = Color.from_hex('#d3d3d3')
lightgreen = Color.from_hex('#90ee90')
lightpink = Color.from_hex('#ffb6c1')
lightsalmon = Color.from_hex('#ffa07a')
lightseagreen = Color.from_hex('#20b2aa')
lightskyblue = Color.from_hex('#87cefa')
lightslategray = Color.from_hex('#778899')
lightslategrey = Color.from_hex('#778899')
lightsteelblue = Color.from_hex('#b0c4de')
lightyellow = Color.from_hex('#ffffe0')
lime = Color.from_hex('#00ff00')
limegreen = Color.from_hex('#32cd32')
linen = Color.from_hex('#faf0e6')
magenta = Color.from_hex('#ff00ff')
maroon = Color.from_hex('#800000')
mediumaquamarine = Color.from_hex('#66cdaa')
mediumblue = Color.from_hex('#0000cd')
mediumorchid = Color.from_hex('#ba55d3')
mediumpurple = Color.from_hex('#9370d8')
mediumseagreen = Color.from_hex('#3cb371')
mediumslateblue = Color.from_hex('#7b68ee')
mediumspringgreen = Color.from_hex('#00fa9a')
mediumturquoise = Color.from_hex('#48d1cc')
mediumvioletred = Color.from_hex('#c71585')
midnightblue = Color.from_hex('#191970')
mintcream = Color.from_hex('#f5fffa')
mistyrose = Color.from_hex('#ffe4e1')
moccasin = Color.from_hex('#ffe4b5')
navajowhite = Color.from_hex('#ffdead')
navy = Color.from_hex('#000080')
oldlace = Color.from_hex('#fdf5e6')
olive = Color.from_hex('#808000')
olivedrab = Color.from_hex('#6b8e23')
orange = Color.from_hex('#ffa500')
orangered = Color.from_hex('#ff4500')
orchid = Color.from_hex('#da70d6')
palegoldenrod = Color.from_hex('#eee8aa')
palegreen = Color.from_hex('#98fb98')
paleturquoise = Color.from_hex('#afeeee')
palevioletred = Color.from_hex('#d87093')
papayawhip = Color.from_hex('#ffefd5')
peachpuff = Color.from_hex('#ffdab9')
peru = Color.from_hex('#cd853f')
pink = Color.from_hex('#ffc0cb')
plum = Color.from_hex('#dda0dd')
powderblue = Color.from_hex('#b0e0e6')
purple = Color.from_hex('#800080')
red = Color.from_hex('#ff0000')
rosybrown = Color.from_hex('#bc8f8f')
royalblue = Color.from_hex('#4169e1')
saddlebrown = Color.from_hex('#8b4513')
salmon = Color.from_hex('#fa8072')
sandybrown = Color.from_hex('#f4a460')
seagreen = Color.from_hex('#2e8b57')
seashell = Color.from_hex('#fff5ee')
sienna = Color.from_hex('#a0522d')
silver = Color.from_hex('#c0c0c0')
skyblue = Color.from_hex('#87ceeb')
slateblue = Color.from_hex('#6a5acd')
slategray = Color.from_hex('#708090')
slategrey = Color.from_hex('#708090')
snow = Color.from_hex('#fffafa')
springgreen = Color.from_hex('#00ff7f')
steelblue = Color.from_hex('#4682b4')
tan = Color.from_hex('#d2b48c')
teal = Color.from_hex('#008080')
thistle = Color.from_hex('#d8bfd8')
tomato = Color.from_hex('#ff6347')
turquoise = Color.from_hex('#40e0d0')
violet = Color.from_hex('#ee82ee')
wheat = Color.from_hex('#f5deb3')
white = Color.from_hex('#ffffff')
whitesmoke = Color.from_hex('#f5f5f5')
yellow = Color.from_hex('#ffff00')
yellowgreen = Color.from_hex('#9acd32')


if __name__ == '__main__':
    print(Color(127))
