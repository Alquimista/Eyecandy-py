#!/usr/bin/env python
# -*- coding: utf-8 -*-
from collections import namedtuple
from copy import copy
from functools import partial
from operator import attrgetter
import re

try:
    from PyQt5 import QtGui, QtCore, QtWidgets
    # start qapplication
    app = QtWidgets.QApplication([])
except ImportError:
    from PyQt4 import QtGui, QtCore
    # start qapplication
    app = QtGui.QApplication([])

try:
    from reader import Reader
    from writer import Writer
    from asstime import Time
    from color import Color

    import helpers

except ImportError:
    from .reader import Reader
    from .writer import Writer
    from .asstime import Time
    from .color import Color

    from . import helpers

RE_TAGS = re.compile(
    r'''
    ({[\s\w\d\\-]+})*           # remove all the tags
                                # {comment}{\be1}{\k86}fai{\k20}ry --> fairy
    ''',
    re.IGNORECASE | re.UNICODE | re.VERBOSE)
RE_KARA = re.compile(
    r'''
    (?<=[\\k|\\ko|\\kf])(?P<duration>\d+)    # k duration in centiseconds
    (?:\-)*(?P<inline>[\w\d]+)*              # inline
    (?:\\[\w\d]+)*                           # ignore tags
    }(?P<text>[^\{\}]*)                      # text
    ''',
    re.IGNORECASE | re.UNICODE | re.VERBOSE)


Resolution = namedtuple('Resolution', 'x, y')


class Text(object):

    """Some attribites of a text"""

    def __init__(self, style, text, ssampling=64):
        self._text = text
        self._style = style
        self._ssampling = ssampling

    @property
    def text(self):
        # Remove Tags
        return re.sub(RE_TAGS, "", self._text)

    @property
    def width(self):
        return self.size[0]

    @property
    def height(self):
        return self.size[1]

    @property
    def size(self):
        """Get width and height of text"""

        # Font
        font = QtGui.QFont(self._style.fontname)
        font.setLetterSpacing(
            QtGui.QFont.AbsoluteSpacing, self._style.spacing)
        font.setHintingPreference(QtGui.QFont.PreferNoHinting)
        font.setStyleStrategy(QtGui.QFont.PreferMatch)
        font.setPixelSize(self._style.fontsize * self._ssampling)
        font.setItalic(self._style.italic)
        font.setBold(self._style.bold)

        # Fontmetric Size
        fontmetrics = QtGui.QFontMetrics(font)
        height = fontmetrics.height()
        width = fontmetrics.width(self.text)

        # VSfilter size
        pixelsize = font.pixelSize()
        scaling = pixelsize / (height if height > 0 else 1)
        width = width * scaling * (self._style.scalex / 100)
        height = pixelsize * (self._style.scaley / 100)

        return (round(width / self._ssampling, 4),
                round(height / self._ssampling, 4))


class Metadata(object):

    """docstring for Metadata"""

    def __init__(self, meta):
        self._title = meta["title"]
        self._original_script = meta["original_script"]
        self._translation = meta["translation"]
        self._timing = meta["timing"]

    title = property(attrgetter("_title"))
    original_script = property(attrgetter("_original_script"))
    translation = property(attrgetter("_translation"))
    timing = property(attrgetter("_timing"))

    def as_dict(self):
        """Return a dict from instance variables"""
        return dict(
            (key, getattr(self, key)) for key in dir(self)
            if not key.startswith("_") and not key == "as_dict")


class Video(object):

    """docstring for Video"""

    def __init__(self, video):
        self._path = video["path"]
        self._zoom = video["zoom"]
        self._position = video["position"]
        self._ar = video["ar"]

    path = property(attrgetter("_path"))
    zoom = property(attrgetter("_zoom"))
    position = property(attrgetter("_position"))
    ar = property(attrgetter("_ar"))

    def as_dict(self):
        """Return a dict from instance variables"""
        return dict(
            (key, getattr(self, key)) for key in dir(self)
            if not key.startswith("_") and not key == "as_dict")


class Dialog(object):

    """Dialogue base object"""

    def __init__(self, dialog, resolution):
        self.resolution = resolution
        self.layer = dialog["layer"]
        self.start = Time.from_strtime(dialog["start"])
        self.end = Time.from_strtime(dialog["end"])
        self.style = Style(dialog["style"]["name"], dialog["style"])
        self.actor = dialog["actor"]
        self.effect = dialog["effect"]
        self.text = dialog["text"]
        self.comment = dialog["comment"]
        self.tag = ""

    def copy(self):
        return copy(self)

    @property
    def dur(self):
        """Dialogue duration"""
        return self.end - self.start

    @property
    def mid(self):
        """Dialog mid time"""
        return self.start + self.dur / 2

    def as_dict(self):
        text = self.text
        if self.tag:
            text = "{" + self.tag + "}" + text
        dialog_item = {
            "layer": self.layer,
            "start": self.start.strtime, "end": self.end.strtime,
            "style": self.style.as_dict(), "actor": self.actor,
            "effect": self.effect, "text": text,
            "comment": self.comment}
        return dialog_item


class Line(Dialog):

    """docstring for Line"""

    def __init__(self, dialog, resolution):
        super(Line, self).__init__(dialog, resolution)

        self._resolution = resolution
        self._rawtext = self.text
        self._asstext = Text(self.style, self.text)
        self.text = self._asstext.text

        self._pos = self._position()    # for alignment in the center an5
        # Line x
        self.left = self._pos[0]
        self.center = self._pos[1]
        self.right = self._pos[2]
        # Line y
        self.top = self._pos[3]
        self.middle = self._pos[4]
        self.bottom = self._pos[5]

        # alias for .center, .middle
        self.x, self.y = self.center, self.middle

        self.syls = self._syls()
        self.chars = self._chars()
        self.char_n = len(self.chars)
        self.syl_n = len(self.syls)

    @property
    def width(self):
        """Pixel Size width of text"""
        return self._asstext.width

    @property
    def height(self):
        """Pixel Size height of text"""
        return self._asstext.height

    @property
    def size(self):
        """Pixel Size width of text"""
        return self._asstext.size

    def _position(self):
        # an7: .left, .top    | an8: .center, .top    | an9: .right, .top
        # an4: .left, .middle | an5: .center, .middle | an6: .right, .middle
        # an1: .left, .bottom | an2: .center, .bottom | an3: .right, .bottom

        align = self.style.alignment
        resx, resy = self._resolution
        mv = self.style.marginv    # margen top/bottom
        ml = self.style.marginl    # margen left
        mr = self.style.marginr    # margen right

        # Alignment
        height = self.height
        width = self.width
        middleheight = height / 2
        middlewidth = width / 2

        # line x
        if align == 1 or align == 4 or align == 7:      # left
            lleft = ml
            lcenter = lleft + middlewidth
            lright = lleft + width
        elif align == 2 or align == 5 or align == 8:    # center
            lcenter = resx / 2
            lleft = lcenter - middlewidth
            lright = lcenter + middlewidth
        elif align == 3 or align == 6 or align == 9:    # right
            lleft = resx - mr - width
            lcenter = lleft + middlewidth
            lright = lleft + width

        # line y
        if align == 7 or align == 8 or align == 9:      # top
            ltop = mv
            lmid = ltop + middleheight
            lbot = ltop + height
        elif align == 4 or align == 5 or align == 6:    # middle
            lmid = resy / 2
            ltop = lmid - middleheight
            lbot = lmid + middleheight
        elif align == 1 or align == 2 or align == 3:    # bottom
            lbot = resy - mv
            lmid = lbot - middleheight
            ltop = lbot - height

        return lleft, lcenter, lright, ltop, lmid, lbot

    def _syls(self):
        """Syllables(karaoke) of the current line"""
        syllabes = []
        line_start = self.start
        line_end = self.end
        sleft = self.left

        re_syls = re.findall(RE_KARA, self._rawtext)
        syl_n = len(re_syls)

        # fix prespace
        #    input: {\k30}ka{\k16} shi
        #    output: {\k30}ka {\k16}shi
        re_syls = [list(syl) for syl in re_syls]
        for i, syl in enumerate(re_syls):
            match = re.match("(\s*)(\w+)(\s*)", list(syl)[-1])
            if match:
                prespace, syltext, postspace = match.groups()
                if prespace:
                    if i > 0:
                        re_syls[i - 1][-1] = re_syls[i - 1][-1] + prespace
                        re_syls[i][-1] = syltext + postspace
                    else:
                        re_syls[i][-1] = syltext

        for i, match in enumerate(re_syls):
            duration, inline, text = match

            # The time in duration is in centisecond
            duration = Time.from_cs(int(duration))
            style = self.style
            actor = self.actor
            effect = self.effect

            width = Text(style, text).width + style._fix_width

            # Absolute times
            start = line_start
            line_start += duration
            if i == syl_n - 1:
                # Ensure that the end time and the width of the last syl
                # is the same that the end time and width of the line
                end = line_end
            else:
                end = line_start

            syl_item = {
                "layer": self.layer,
                "start": start.strtime, "end": end.strtime,
                "style": style.as_dict(), "actor": actor, "inline": inline,
                "effect": effect, "text": text.strip(), "comment": False}

            syllabes.append(Syl(syl_item, self.resolution, sleft))
            sleft += width

        return syllabes

    def _chars(self):
        charas = []
        n = 1
        for i, s in enumerate(self.syls):

            cleft = s.left
            line_start = s.start
            line_end = s.end

            char_n = len(s.text)

            # For syls of one char
            if char_n == 1 or char_n == 0:
                duration = s.dur
            else:
                duration = Time(int(round(s.dur.ms / char_n, 0)))

            for ci, char in enumerate(s.text):

                start = line_start
                line_start += duration

                width = Text(s.style, char).width + self.style._fix_width

                if ci == char_n - 1:
                    # Ensure that the end time and the width of the last char
                    # is the same that the end time and width of the syl
                    end = line_end
                else:
                    end = line_start

                char_item = {
                    "layer": s.layer,
                    "start": start.strtime, "end": end.strtime,
                    "style": s.style.as_dict(), "actor": s.actor,
                    "inline": s.inline,
                    "effect": s.effect, "text": char.strip(),
                    "comment": False,
                    "sylstart": s.start,
                    "sylend": s.end,
                }

                charas.append(Char(char_item, self.resolution, cleft))
                cleft += width

        return charas


class Syl(Line):

    """docstring for Syl"""

    def __init__(self, dialog, resolution, sleft):
        super(Syl, self).__init__(dialog, resolution)
        self.inline = dialog["inline"]
        self.left = sleft
        self.center = self.left + self.width / 2
        self.right = self.left + self.width
        self.x, self.y = self.center, self.middle


class Char(Line):

    """docstring for Char"""

    def __init__(self, dialog, resolution, cleft):
        super(Char, self).__init__(dialog, resolution)
        self.left = cleft
        self.inline = dialog["inline"]
        self.center = self.left + self.width / 2
        self.right = self.left + self.width
        self.x, self.y = self.center, self.middle

        self.sylstart = dialog["sylstart"]
        self.sylend = dialog["sylend"]


class Style(object):

    """Style Object"""

    def __init__(self, name, style):
        self._name = name
        self._fontname = style["font"]["name"]
        self._fontsize = style["font"]["size"]
        self._primarycolor = Color.from_ass(style["color"]["primary"])
        self._secondarycolor = Color.from_ass(style["color"]["secondary"])
        self._bordcolor = Color.from_ass(style["color"]["bord"])
        self._shadowcolor = Color.from_ass(style["color"]["shadow"])
        self._bold = style["bold"]
        self._italic = style["italic"]
        self._scalex = style["scale"][0]
        self._scaley = style["scale"][1]
        self._spacing = style["spacing"]
        self._bord = style["bord"]
        self._shadow = style["shadow"]
        self._alignment = style["alignment"]
        self._marginl = style["margin"]["l"]
        self._marginr = style["margin"]["r"]
        self._marginv = style["margin"]["v"]
        self._fix_width = style.get("fix_width", 0)

    name = property(attrgetter("_name"))
    fontname = property(attrgetter("_fontname"))
    fontsize = property(attrgetter("_fontsize"))
    primarycolor = property(attrgetter("_primarycolor"))
    secondarycolor = property(attrgetter("_secondarycolor"))
    bordcolor = property(attrgetter("_bordcolor"))
    shadowcolor = property(attrgetter("_shadowcolor"))
    bold = property(attrgetter("_bold"))
    italic = property(attrgetter("_italic"))
    scalex = property(attrgetter("_scalex"))
    scaley = property(attrgetter("_scaley"))
    spacing = property(attrgetter("_spacing"))
    bord = property(attrgetter("_bord"))
    shadow = property(attrgetter("_shadow"))
    alignment = property(attrgetter("_alignment"))
    marginl = property(attrgetter("_marginl"))
    marginr = property(attrgetter("_marginr"))
    marginv = property(attrgetter("_marginv"))

    @property
    def scale(self):
        return self.scalex, self.scaley

    def as_dict(self):
        """Return a dict from instance variables"""
        style_item = {
            "name": self.name,
            "font": {"name": self.fontname, "size": self.fontsize},
            "color": {"primary": self.primarycolor.ass_long,
                      "secondary": self.secondarycolor.ass_long,
                      "bord": self.bordcolor.ass_long,
                      "shadow": self.shadowcolor.ass_long},
            "bold": self.bold, "italic": self.italic,
            "scale": [self.scalex, self.scaley],
            "spacing": self.spacing, "bord": self.bord,
            "shadow": self.shadow, "alignment": self.alignment,
            "margin": {"l": self.marginl, "r": self.marginr,
                       "v": self.marginv}}
        return style_item

    def __eq__(self, other):
        if isinstance(other, Style):
            sty2 = other.name
        else:
            sty2 = other
        return self.name == sty2

    def __ne__(self, other):
        if isinstance(other, Style):
            sty2 = other.name
        else:
            sty2 = other
        return not self.name == sty2


class Generator(object):

    """docstring for Generator"""

    def __init__(self, input_script, output_script=None, progressbar=True,
                 original=True, open=True):
        self._input_script = input_script
        self._output_script = output_script
        self.progressbar = progressbar
        self._script_data = Reader().read(self._input_script)
        self.open = open

        self._dialog = []

        self.kara_n = len(list(self.lines))

        # Add default Style
        try:
            self.get_style("Default")
        except KeyError:
            self.add_style()
        # Add default commented Dialog
        if original:
            self._add_default_dialog()

    input_script = property(attrgetter("_input_script"))
    output_script = property(attrgetter("_output_script"))

    @property
    def audio(self):
        return self._script_data["audio"]

    @audio.setter
    def audio(self, audio):
        self._script_data["audio"] = audio

    @property
    def resolution(self):
        return Resolution(*self._script_data["resolution"])

    @resolution.setter
    def resolution(self, resolution):
        self._script_data["resolution"] = resolution

    @property
    def video(self):
        return Video(self._script_data["video"])

    def add_video(self, path=None, zoom=None,
                  position=None, ar=None):
        if path:
            self._script_data["video"]["path"] = path
        if zoom:
            self._script_data["video"]["zoom"] = zoom
        if position:
            self._script_data["video"]["position"] = position
        if ar:
            self._script_data["video"]["ar"] = ar

    @property
    def metadata(self):
        return Metadata(self._script_data["metadata"])

    def add_metadata(self, title=None, original_script=None,
                     translation=None, timing=None):
        if title:
            self._script_data["metadata"]["title"] = title
        if original_script:
            self._script_data["metadata"]["original_script"] = original_script
        if translation:
            self._script_data["metadata"]["translation"] = translation
        if timing:
            self._script_data["metadata"]["timing"] = timing

    def get_style(self, name):
        return Style(name, self._script_data["style"][name])

    def style_fix_width(self, fix_width, name=None):
        if name:
            self._script_data["style"][name]["fix_width"] = fix_width
        else:
            for style in self._script_data["style"]:
                self._script_data["style"][style][
                    "fix_width"] = fix_width

    @property
    def styles(self):
        styles = []
        for key in self._script_data["style"]:
            styles.append(self.get_style(key))
        return styles

    def add_style(self, name="Default", fontname="Arial", fontsize=20,
                  primarycolor="fff", secondarycolor="fff",
                  bordcolor="000", shadowcolor="000",
                  bold=False, italic=False, scalex=100, scaley=100,
                  spacing=0, bord=2, shadow=0, alignment=2,
                  marginl=10, marginr=20, marginv=10):
        if not isinstance(primarycolor, Color):
            primarycolor = Color.from_hex(primarycolor)
        if not isinstance(secondarycolor, Color):
            secondarycolor = Color.from_hex(secondarycolor)
        if not isinstance(bordcolor, Color):
            bordcolor = Color.from_hex(bordcolor)
        if not isinstance(shadowcolor, Color):
            shadowcolor = Color.from_hex(shadowcolor)
        style_item = {
            "name": name,
            "font": {"name": fontname, "size": fontsize},
            "color": {
                "primary": primarycolor.ass_long,
                "secondary": secondarycolor.ass_long,
                "bord": bordcolor.ass_long,
                "shadow": shadowcolor.ass_long},
            "bold": bold, "italic": italic, "scale": [scalex, scaley],
            "spacing": spacing, "bord": bord,
            "shadow": shadow, "alignment": alignment,
            "margin": {"l": marginl, "r": marginr, "v": marginv}}
        self._script_data["style"][name] = style_item

    @property
    def dialogs(self):
        D = partial(Dialog, resolution=self.resolution)
        dialogs = [D(d) for d in self._script_data[
            "dialog"] if d["comment"] == False]
        if self.progressbar:
            return helpers.progressbar(dialogs)
        return dialogs

    def add(self, d):
        self._dialog.append(d.as_dict())

    def add_dialog(self, layer=0, start=0, end=5000,
                   style=None, actor="", effect="", text="",
                   tag="", comment=False):
        if not isinstance(start, Time):
            start = Time(start)
        if not isinstance(end, Time):
            end = Time(end)
        if not style:
            style = self.get_style("Default").as_dict()
        else:
            style = style.as_dict()
        dialog_item = {
            "layer": layer,
            "start": start.strtime, "end": end.strtime,
            "style": style, "actor": actor,
            "effect": effect, "text": text, "comment": comment}
        d = Dialog(dialog_item, self.resolution)
        d.tag = tag
        self.add(d)

    @property
    def lines(self):
        L = partial(Line, resolution=self.resolution)
        lines = [L(l) for l in self._script_data[
            "dialog"] if l["comment"] == False]
        if self.progressbar:
            return helpers.progressbar(lines)
        return lines

    def _add_default_dialog(self):
        """Add the original karaoke commented by default in the script"""
        # This help to jump to the wanted line in the preview in Aegisub,
        # and/or keep a backup of the timed subs
        self.add_dialog(text='### Original Karaoke ###', comment=True)
        for d in self.dialogs:
            d.comment = True
            self.add(d)
        self.add_dialog(text='### Karaoke Effect ###', comment=True)

    def tostring(self):
        # FIX: Don't change alignment in rawlines
        for name in self._script_data["style"].keys():
            self._script_data["style"][name]["alignment"] = 5
        self._script_data["dialog"] = self._dialog
        return Writer(self._script_data)._tostring()

    def save(self, filename=None):
        # FIX: Don't change alignment in rawlines
        if not filename:
            filename = self._output_script
        for name in self._script_data["style"].keys():
            self._script_data["style"][name]["alignment"] = 5
        self._script_data["dialog"] = self._dialog
        Writer(self._script_data).save(filename)
        if self.open:
            helpers.start_file(filename)


# class Fx():
#     def OnDialogue(self, diag):
#         pass
#     def OnSyllable(self, sil):
#         pass
#     def OnLetter(self, let):
#         pass
#     def OnSyllableDead(self, sil):
#         pass
#     def OnSyllableSleep(self, sil):
#         pass
#     def OnLetterDead(self, let):
#         pass
#     def OnLetterSleep(self, let):
#         pass
#     def OnDialogueIn(self, diag):
#         pass
#     def OnSyllableIn(self, sil):
#         pass
#     def OnLetterIn(self, let):
#         pass
#     def OnDialogueOut(self, diag):
#         pass
#     def OnSyllableOut(self, sil):
#         pass
#     def OnLetterOut(self, let):
#         pass


@helpers.timeit
def main():

    import interpolate
    import random
    import color

    it_custom = partial(interpolate.cosine, repeat=6)

    sub = Generator("../tests/test.ass",
                    "../tests/test_writer.ass")

    # an7: .left, .top    | an8: .center, .top    | an9: .right, .top
    # an4: .left, .middle | an5: .center, .middle | an6: .right, .middle
    # an1: .left, .bottom | an2: .center, .bottom | an3: .right, .bottom

    for line in sub.lines:

        c1 = line.style.primarycolor
        c2 = line.style.secondarycolor
        c3 = line.style.bordcolor
        c4 = line.style.shadowcolor

        cblue = color.Color.from_hex("#93BEC2")
        colorsb = list(cblue.gradient(c1, len(line.chars), it_custom))
        i_custom = list(interpolate.interpolate_range(
            0, 1, line.char_n, it_custom))

        for li, char in enumerate(line.chars):
            # alias for .center, .middle
            x, y = char.left, char.bottom

            # Efecto de silaba
            ch = char.copy()
            ch.tag = (pos(x, y) + blur() + c(c2) + fsc(130) +
                      t(fsc(100) + blur(2) + c(colorsb[li])) + an(1))
            ch.layer = 1
            ch.end = char.end + 50
            if ch.end.ms >= line.end.ms:
                ch.end = char.end
            sub.add(ch)

            # Silabas por cantar
            ch = char.copy()
            ch.tag = pos(x, y) + c(c2) + blur() + an(1)
            ch.start = line.start
            ch.end = char.start
            sub.add(ch)

            # Silabas Muertas (cantadas)
            ch = char.copy()
            ch.tag = pos(x, y) + blur() + an(1) + c(colorsb[li])
            ch.start = char.end + 50
            if ch.start.ms >= line.end.ms:
                ch.start = char.end
            ch.end = line.end
            sub.add(ch)

            # Efecto de entrada
            ch = char.copy()
            px = x + random.randint(-5, 5)
            py = y + random.randint(-5, 5)
            m = move(px, py * i_custom[li] - char.height / 4, x, y)
            ch.tag = blur() + fad(150, 0) + c(c2) + m + an(1)
            ch.start = line.start - 100
            ch.end = line.start
            sub.add(ch)

            # Efecto de salida
            ch = char.copy()
            m = move(x, y, px, py + char.height / 2)
            ch.tag = blur() + fad(0, 150) + c(colorsb[li]) + m + an(1)
            ch.start = line.end
            ch.end = line.end + 100
            sub.add(ch)

    sub.save()


if __name__ == '__main__':
    from pprint import pprint

    from asstags import *
    main()
