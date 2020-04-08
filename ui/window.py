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

import pod

import os

from utils import *
import pod
from .box import *
from .combo import *
from .eq import *
from .presetlist import PresetList
from importl6t import ImportL6T

class Window:
    __gtype_name__ = 'Window'

    def __init__(self):
        self.boxes = {}

        self.glade = Gtk.Builder()
        self.glade.add_objects_from_file("line6control.glade", ("MainWindow",))
        self.glade.connect_signals({
            'previous_channel_cb' : self.previous_channel_cb,
            'next_channel_cb' : self.next_channel_cb,
            'on_open_file_activate' : self.open_file_cb})

        self.main_window = self.glade.get_object("MainWindow")
        self.main_window.connect('delete-event', self.do_delete_event)

        self.presetid = self.glade.get_object("PresetIDLabel")
        self.presetname = self.glade.get_object("PresetNameLabel")

        self.prev_channel = self.glade.get_object("PreviousButton")
        self.next_channel = self.glade.get_object("NextButton")

        p = pod.Pod.get()

        self.presetlist = PresetList()
        self.glade.get_object("PresetListScrolledWindow").add(self.presetlist)
        self.presetlist.show()

        if p.device in AmpBox.base_model:
            self.boxes['ampbox'] = AmpBox(p.device)
            self.glade.get_object("AmpBox").add(self.boxes['ampbox'])
            self.boxes['ampcombobox'] = AmpComboBox(p.device)
            self.glade.get_object("AmpBox").add(self.boxes['ampcombobox'])

        if p.device in CabBox.base_model:
            self.boxes['cabbox'] = CabBox(p.device)
            self.glade.get_object("CabBox").add(self.boxes['cabbox'])
            self.boxes['cabcombobox'] = CabComboBox(p.device)
            self.glade.get_object("CabBox").add(self.boxes['cabcombobox'])

        if p.device in StompBox.base_model:
            self.boxes['stompbox'] = StompBox(p.device)
            self.glade.get_object("StompBox").add(self.boxes['stompbox'])
            self.boxes['stompcombobox'] = StompComboBox(p.device)
            self.glade.get_object("StompBox").add(self.boxes['stompcombobox'])
        elif p.device in EffectBox.base_model:
            self.boxes['effectbox'] = EffectBox(p.device)
            self.glade.get_object("StompBox").add(self.boxes['effectbox'])
            self.boxes['effectcombobox'] = EffectComboBox(p.device)
            self.glade.get_object("StompBox").add(self.boxes['effectcombobox'])

        if p.device in NoiseGateBox.base_model:
            self.boxes['gate'] = NoiseGateBox(p.device)
            self.glade.get_object("HBox3").add(self.boxes['gate'])

        if p.device in CompBox.base_model:
            self.boxes['comp'] = CompBox(p.device)
            self.glade.get_object("HBox2").add(self.boxes['comp'])

        if p.device in ModBox.base_model:
            self.boxes['modbox'] = ModBox(p.device)
            self.glade.get_object("ModBox").add(self.boxes['modbox'])
            self.boxes['modcombobox'] = ModComboBox(p.device)
            self.glade.get_object("ModBox").add(self.boxes['modcombobox'])

        if p.device in DelayBox.base_model:
            self.boxes['delaybox'] = DelayBox(p.device)
            self.glade.get_object("DelayBox").add(self.boxes['delaybox'])
            self.boxes['delaycombobox'] = DelayComboBox(p.device)
            self.glade.get_object("DelayBox").add(self.boxes['delaycombobox'])

        self.boxes['eqbox'] = EQBox()
        self.glade.get_object("MainVBox").add(self.boxes['eqbox'])

        for e in self.boxes:
            self.boxes[e].show()

    def presets_changed(self, presets):
        if presets != None:
            for e in presets:
                if e in self.boxes:
                    self.boxes[e].changed()
        else:
            for e in self.boxes:
                self.boxes[e].changed()

        p = pod.Pod.get()
        self.presetid.set_text("%d%s" % (p.pid / 4 + 1, chr(p.pid % 4 + 65)))
        self.presetname.set_text(p.patches[p.pid].presetname)

        self.prev_channel.set_sensitive(p.pid > 0)
        self.next_channel.set_sensitive(p.pid < p.channel_count)

    def do_delete_event(self, widget, ev):
        pod.Pod.get().close()
        Gtk.main_quit()

    def previous_channel_cb(self, obj):
        curid = pod.Pod.get().pid
        if curid > 0:
            pod.Pod.get().set_channel(curid - 1)

    def next_channel_cb(self, obj):
        curid = pod.Pod.get().pid
        if curid < pod.Pod.get().channel_count:
            pod.Pod.get().set_channel(curid + 1)

    def open_file_cb(self, obj):
        fd = Gtk.FileSelection("File selection")
        fd.connect("destroy", lambda w: fd.destroy())

        fd.ok_button.connect("clicked", self.open_file_ok_cb, fd)
        fd.cancel_button.connect("clicked", lambda w: fd.destroy())

        fd.show()

    def open_file_ok_cb(self, w, fd):
        filename = fd.get_filename()
        fd.destroy()

        size = int(os.stat(filename)[6])
        if size == 160: # it's a dump file
            debug_msg("Found DUMP file...")
            fd = open(filename)
            buf = fd.read()
            fd.close()

            pod.Pod.get().set_current_patch(buf)

    def open_l6t_file_cb(self, obj):
        i = ImportL6T("marshall-jcm800.l6t")
        i.parse()
        print(i.buffer)
