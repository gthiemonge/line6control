#!/usr/bin/env python
#
#  Copyright (C) 2006  Gregory Thiemonge
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License as
#  published by the Free Software Foundation; either version 2 of the
#  License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307
#  USA

import os
import sys

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository.GdkPixbuf import Pixbuf
import cairo

class Resources:
    __instance = None

    @classmethod
    def _root_directories(cls):
        yield os.path.join(sys.prefix, "share", "line6control")
        yield os.path.join("line6control", "data")
        yield os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           "..", "data")

    @classmethod
    def get_root_directory(cls):
        for path in cls._root_directories():
            if os.path.isdir(path):
                return path
        return None

    def __init__(self):
        Resources.__instance = self

        filename = os.path.join(Resources.get_root_directory(),
                                "knob_bg.png")
        self.knob_background = cairo.ImageSurface.create_from_png(filename)

        filename = os.path.join(Resources.get_root_directory(),
                                "knob.png")
        self.knob_pix = cairo.ImageSurface.create_from_png(filename)

        filename = os.path.join(Resources.get_root_directory(),
                                "switch.png")
        self.switch = cairo.ImageSurface.create_from_png(filename)

    @classmethod
    def get(cls):
        if not cls.__instance:
            Resources()
        return cls.__instance
