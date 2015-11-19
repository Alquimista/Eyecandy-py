#!/usr/bin/env python
# -*- coding: utf-8 -*-
import codecs
import os

try:
    import asstime
    import helpers
except ImportError:
    from . import asstime
    from . import helpers


STYLE_FORMAT = (
    "Name", "Fontname", "Fontsize", "PrimaryColour", "SecondaryColour",
    "OutlineColour", "BackColour", "Bold", "Italic", "Underline",
    "StrikeOut", "ScaleX", "ScaleY", "Spacing", "Angle", "BorderStyle",
    "Outline", "Shadow", "Alignment", "MarginL", "MarginR",
    "MarginV", "Encoding")
DIALOG_FORMAT = (
    "Layer", "Start", "End", "Style", "Name", "MarginL",
    "MarginR", "MarginV", "Effect", "Text")
_ASSBOOL = {True: "-1", False: "0"}


class Writer(object):

    def __init__(self, assdict, filename=None):
        self._filename = filename
        self._assdict = assdict
        self._defaults()  # Move to effector

    def _defaults(self):
        # Default values
        # Default resolution if resolution is not present
        if not all(self._assdict["resolution"]):
            self._assdict["resolution"] = [640, 480]
        if not self._assdict["style"]:
            self._assdict["style"] = {
                "Default": {
                    "font": {"name": "Arial", "size": 20},
                    "color": {
                        "primary": "&H00FFFFFF",
                        "secondary": "&H00FFFFFF",
                        "bord": "&H00000000",
                        "shadow": "&H00000000"},
                    "bold": False, "italic": False,
                    "scale": [100, 100],
                    "spacing": 0,
                    "bord": 2, "shadow": 0,
                    "alignment": 2,
                    "margin": {"l": 10, "r": 20, "v": 10}}}
        if not self._assdict["dialog"]:
            self._assdict["dialog"] = [{
                "layer": 0,
                "start": "0:00:00.00", "end": "0:05:00.00",
                "style": self._assdict["style"]["Default"],
                "autor": "", "effect": "", "text": "",
                "comment": False}]

    def _dialog(self):
        dialog_fmt = []
        for dialog in helpers.progressbar(
                self._assdict["dialog"], prefix='Writing'):
            if dialog["comment"]:
                key = "Comment"
            else:
                key = "Dialogue"
            if dialog["text"]:
                dialog_fmt.append(
                    "{:s}: {:d},{:s},{:s},{:s},{:s},{:s},{:s},{:s},{:s},"
                    "{:s}".format(
                        key,
                        dialog["layer"],
                        dialog["start"],
                        dialog["end"],
                        dialog["style"]["name"],
                        dialog["actor"],
                        "0000", "0000", "0000",  # marginl, marginr, marginv
                        dialog["effect"],
                        dialog["text"]))
        return "\n".join(dialog_fmt)

    def _format(self, values):
        return 'Format: {:s}'.format(', '.join(values))

    def _style(self):
         # List only used styles in the dialog
        dialog_styles = set()
        for d in self._assdict["dialog"]:
            style_name = d["style"]["name"]
            dialog_styles.add(style_name)
        styles = []
        for sty_name in dialog_styles:
            sty = self._assdict["style"][sty_name]
            styles.append(
                "Style: {:s},{:s},{:d},{:s},{:s},{:s},{:s},{:s},{:s},{:s},"
                "{:s},{:f},{:f},{:d},{:s},{:s},{:f},{:f},{:d},{:04d},{:04d},"
                "{:04d},{:s}".format(
                    sty["name"],
                    sty["font"]["name"],
                    sty["font"]["size"],
                    sty["color"]["primary"],
                    sty["color"]["secondary"],
                    sty["color"]["bord"],
                    sty["color"]["shadow"],
                    # change flags -1, 0, to a bool type
                    _ASSBOOL[sty["bold"]],
                    _ASSBOOL[sty["italic"]],
                    "0",  # underline
                    "0",  # strikeout
                    sty["scale"][0],  # scalex
                    sty["scale"][1],  # scaley
                    sty["spacing"],
                    "0",  # angle
                    "1",  # opaque box
                    sty["bord"],  # bord
                    sty["shadow"],
                    sty["alignment"],
                    sty["margin"]["l"],
                    sty["margin"]["r"],
                    sty["margin"]["v"],
                    "0"))
        return "\n".join(styles)

    def _metadata(self):
        meta = []
        title = self._assdict["metadata"]["title"]
        original_script = self._assdict["metadata"]["original_script"]
        translation = self._assdict["metadata"]["translation"]
        timing = self._assdict["metadata"]["timing"]
        if not title:
            meta.append("Title: Default Eyecandy file")
        else:
            meta.append("Title: {}".format(title))
        if original_script:
            meta.append("Original Script: {}".format(original_script))
        else:
            meta.append(
                "Original Script: {}".format(
                    os.path.basename(self._assdict["metadata"]["filename"])))
        if translation:
            meta.append("Translation: {}".format(translation))
        if timing:
            meta.append("Timing: {}".format(timing))
        return "\n".join(meta)

    def _aegisub(self):
        aegisub = []
        if self._assdict["video"]["path"]:
            aegisub.append("Video File: {:s}".format(
                self._assdict["video"]["path"]))
            if self._assdict["video"]["zoom"]:
                aegisub.append("Video Zoom Percent: {:06f}".format(
                    self._assdict["video"]["zoom"]))
            if self._assdict["video"]["ar"]:
                aegisub.append("Video AR Mode: 4")
                aegisub.append("Video AR Value: {:.06f}".format(
                    self._assdict["video"]["ar"]))
            if self._assdict["video"]["position"]:
                aegisub.append("Video Position: {:d}".format(
                    self._assdict["video"]["position"]))
        else:
            # Dummy video
            framerate = round(asstimr.FPS_NTSC_FILM, 3)
            w, h = self._assdict["resolution"]
            r, g, b = (0, 0, 0)
            checkboard = ""  # checkbord=True "c", checkboard=False ""
            frames = asstime.strtime_to_frames(
                self._assdict["dialog"][-1]["end"])
            video = '?dummy:{:.6f}:{:d}:{:d}:{:d}:{:d}:{:d}:{:d}{:s}:'.format(
                framerate, frames, w, h, r, g, b, checkboard)
            aegisub.append("Video Position: {:s}".format(video))

        if self._assdict["audio"]:
            aegisub.append("Audio File: {}".format(self._assdict["audio"]))
        elif self._assdict["video"]["path"]:
            if self._assdict["video"]["path"].startswith("?dummy"):
                # silence?, noise?
                audio = "dummy-audio:silence?sr=44100&bd=16&ch=1&ln=396900000:"
                aegisub.append("Audio File: {:s}".format(audio))
            else:
                aegisub.append("Audio File: {}".format(
                    self._assdict["video"]["path"]))

        return "\n".join(aegisub)

    def _resolution(self):
        return "PlayResX: {:d}\nPlayResY: {:d}".format(
            *self._assdict["resolution"])

    def _tostring(self):
        ass = (
            "[Script Info]\n"
            "; Script generated by Eyecandy\n"
            "ScriptType: v4.00+\n"
            "{meta}\n"
            "{resolution}\n"
            "WrapStyle: 2\n"
            "ScaledBorderAndShadow: yes\n"
            "YCbCr Matrix: TV.601\n"  # Adjust Aegisub Rendering to VSFilter
            "\n[Aegisub Project Garbage]\n"
            "{aegisub}\n"
            "\n[V4+ Styles]\n"
            "{style_format}\n"
            "{styles}\n"
            "\n[Events]\n"
            "{dialog_format}\n"
            "{dialogs}\n\n").format(
                meta=self._metadata(),
                resolution=self._resolution(),
                aegisub=self._aegisub(),
                styles=self._style(),
                dialogs=self._dialog(),
                style_format=self._format(STYLE_FORMAT),
                dialog_format=self._format(DIALOG_FORMAT))
        return ass

    def save(self, filename=None):
        """"Save to file the ASS script

        Parameters:
        :param filename: filename of the script to read
        """
        if not filename:
            filename = self._filename
        with codecs.open(filename, "wb", "utf-8-sig") as f:
            f.write(self._tostring())

    def __repr__(self):
        return "<class '{:s}'>".format(self.__class__.__name__)
