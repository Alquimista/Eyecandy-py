#!/usr/bin/env python
# -*- coding: utf-8 -*-
import codecs
import sys

try:
    import helpers
except ImportError:
    from . import helpers

COMMENT_CHARS = [";", "!:"]
VIDEO_ZOOM = {'12.5%': 1, '25%': 2, '37.5%': 3, '50%': 4, '62.5%': 5, '75%': 6,
              '87.5%': 7, '100%': 8, '125.5%': 9, '137.5%': 10, '150%': 11,
              '162.5%': 12, '175%': 13, '187.5%': 14, '200%': 15}
VIDEO_ZOOM_INV = {
    1: '0.125000', 2: '0.250000', 3: '0.375000', 4: '0.500000',
    5: '0.625000', 6: '0.750000', 7: '0.875000', 8: '1.000000',
    9: '1.255000', 10: '1.375000', 11: '1.500000', 12: '1.625000',
    13: '1.750000', 14: '1.875000', 15: '2.000000'}


class Reader(object):

    """Simple ASS reader

    Parameters:
    :param filename: filename of the script to read
    """

    def __init__(self, filename=None):
        self._filename = filename

    def _open(self, filename):
        """Open the ASS script file

        Parameters:
        :param filename: filename of the script to read
        """
        filename = filename if filename else self._filename
        error = ("*%s* does not exist, try again with "
                 "another file") % (filename)
        try:
            file = codecs.open(filename, "rb", "utf-8-sig")
        except IOError:
            raise IOError(error)
        return file

    def read(self, filename=None):
        """Read an parse the ass script

        Parameters:
        :param filename: filename of the script to read
        """
        temp_dialog = []
        style = {}

        # Audio & Video Data
        video, video_zoom, video_position, video_aspect_ratio = (
            None, None, None, None)
        playresx, playresy = None, None
        audio = None

        # Metadta
        title, original_script, translation, timing = None, None, None, None

        assfile = self._open(filename)
        SKIP_CHARS = COMMENT_CHARS[:]
        SKIP_CHARS.append("[")
        for line in helpers.progressbar(
                assfile.readlines(), prefix='Reading', sufix='Lines'):
            line = line.strip()
            if line.startswith(tuple(SKIP_CHARS)) or not line:
                continue
            else:
                key, value = line.split(":", 1)
                key = key.lower().replace("+", "p").replace(" ", "_")
                value = value.strip()
                # Dialogue, Comment, Style
                if key == "dialogue" or key == "comment":
                    value = value.split(",", 9)
                    text = value[9]
                    if not text:  # Skip on Empty dialog
                        continue
                    dialog_item = {
                        "layer": int(value[0]),
                        "start": value[1],
                        "end": value[2],
                        "style": value[3],
                        # marginl, marginr, marginl = "0000"
                        "actor": value[4],
                        "effect": value[8],
                        "text": text,
                        "comment": key == "comment",  # commented (True/False)
                    }
                    temp_dialog.append(dialog_item)
                elif key == "style":
                    value = value.split(",", 22)
                    style_item = {
                        "name": value[0],
                        "font": {
                            "name": value[1],
                            "size": int(value[2])},
                        "color": {
                            "primary": value[3],
                            "secondary": value[4],
                            "bord": value[5],
                            "shadow": value[6]},
                        "bold": bool(int(value[7])),
                        "italic": bool(int(value[8])),
                        # Underline, StrikeOut = False (-1)
                        "scale": [float(value[11]), float(value[12])],
                        "spacing": int(value[13]),
                        # Angle = 0
                        # BorderStyle = 1 (Border + Shadow)
                        "bord": float(value[16]),
                        "shadow": float(value[17]),
                        "alignment": int(value[18]),
                        "margin": {
                            "l": int(value[19]),
                            "r": int(value[20]),
                            "v": int(value[21])},
                        # Encoding = 0,
                    }
                    style[value[0]] = style_item
                elif key == "playresx":
                    playresx = int(value)
                elif key == "playresy":
                    playresy = int(value)
                elif key == "video_file":
                    video = value
                elif key == "audio_uri" or key == "audio_file":
                    audio = value
                elif key == "video_zoom" or key == "video_zoom_percent":
                    video_zoom = value
                elif (key == "video_aspect_ratio" or key == "video_ar_value" or
                        key == "aegisub_video_aspect_ratio"):
                    video_aspect_ratio = value.replace("c", "")
                elif key == "title":
                    title = value
                elif key == "original_script":
                    original_script = value
                elif key == "translation":
                    translation = value
                elif key == "timing":
                    timing = value
                elif key == "video_position":
                    video_position = int(value)
                else:
                    continue
        assfile.close()

        # Add style to dialogs
        dialog = []
        if temp_dialog:
            for d in temp_dialog:
                d["style"] = style[d["style"]]
                dialog.append(d)
        else:
            dialog = None

        try:
            video_zoom = VIDEO_ZOOM_INV[VIDEO_ZOOM[video_zoom]]
        except KeyError:
            video_zoom = float(video_zoom)

        try:
            num, den = video_aspect_ratio.split(':')
            video_aspect_ratio = float(num / den)
        except ValueError:
            video_aspect_ratio = float(video_aspect_ratio)

        # Default values: None
        ass = {
            "dialog": dialog,
            "style": style,
            "resolution": [playresx, playresy],
            "video": {
                "path": video,
                "zoom": video_zoom,
                "position": video_position,
                "ar": video_aspect_ratio,
            },
            "audio": audio,
            "metadata": {
                "filename": filename,
                "title": title,
                "original_script": original_script,
                "translation": translation,
                "timing": timing,
            }
        }
        return ass

    def __repr__(self):
        return "<class '{:s}'>".format(self.__class__.__name__)
