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

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gi.repository import GObject

from .window import *

class WaitWindow(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self) # XXX , Gtk.WINDOW_POPUP)
        #self.set_position(Gtk.WIN_POS_CENTER_ALWAYS)

        self.set_title("Line 6 Control")

        self.set_border_width(10)
        self.set_size_request(250, 70)

        vbox = Gtk.VBox(False, 5)

        label1 = Gtk.Label("Please wait, retrieving POD presets...")
        vbox.add(label1)

        self.progressbar = Gtk.ProgressBar()
        vbox.add(self.progressbar)

        self.add(vbox)

        self.show_all()

class Interface:
    __instance = None
    def __init__(self):
        Interface.__instance = self

        GObject.timeout_add(100, self.check_presetlist_done)

        self.wait = WaitWindow()
        self.win = None

    @classmethod
    def get(cls):
        return cls.__instance

    def run(self):
        self.win = Window()
        self.wait.destroy()

        return False

    def check_presetlist_done(self):
        p = pod.Pod.get()
        npatches = len(p.patches)

        if npatches > p.channel_count:
            GObject.idle_add(self.run)
            return False

        if npatches != 0:
            self.wait.progressbar.set_fraction(float(npatches) / 127.0)
            try:
                str = p.patches[p.pid].presetname
                self.wait.progressbar.set_text(str)
            except KeyError:
                pass

        return True

    def add_preset(self, pid, podid, preset_name):
        self.win.presetlist.add_elem(pid, podid, preset_name)

    def presets_changed(self, presets):
        if self.win == None:
            GObject.timeout_add(100, self.presets_changed, presets)
            return False

        self.win.presets_changed(presets)

        return False
