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

import pygtk
pygtk.require('2.0')
import gtk
import gtk.glade
import gobject

import os

from utils import *
import pod
from box import *
from combo import *
from eq import *
from presetlist import PresetList
from importl6t import ImportL6T

class Window:
    __gtype_name__ = 'Window'

    def __init__(self):
        self.boxes = {}
        
        self.glade = gtk.glade.XML("line6control.glade", "MainWindow")
        self.glade.signal_autoconnect({
            'previous_channel_cb' : self.previous_channel_cb,
            'next_channel_cb' : self.next_channel_cb,
            'on_open_file_activate' : self.open_file_cb})
        
        self.main_window = self.glade.get_widget("MainWindow")
        self.main_window.connect('delete-event', self.do_delete_event)
        
        self.presetid = self.glade.get_widget("PresetIDLabel")
        self.presetname = self.glade.get_widget("PresetNameLabel")
        
        self.prev_channel = self.glade.get_widget("PreviousButton")
        self.next_channel = self.glade.get_widget("NextButton")

        self.presetlist = PresetList()
        self.glade.get_widget("PresetListScrolledWindow").add(self.presetlist)
        self.presetlist.show()

        self.boxes['ampbox'] = AmpBox()
        self.glade.get_widget("AmpBox").add(self.boxes['ampbox'])
        self.boxes['ampcombobox'] = AmpComboBox()
        self.glade.get_widget("AmpBox").add(self.boxes['ampcombobox'])

        self.boxes['cabbox'] = CabBox()
        self.glade.get_widget("CabBox").add(self.boxes['cabbox'])
        self.boxes['cabcombobox'] = CabComboBox()
        self.glade.get_widget("CabBox").add(self.boxes['cabcombobox'])

        self.boxes['stompbox'] = StompBox()
        self.glade.get_widget("StompBox").add(self.boxes['stompbox'])
        self.boxes['stompcombobox'] = StompComboBox()
        self.glade.get_widget("StompBox").add(self.boxes['stompcombobox'])

        self.boxes['gate'] = NoiseGateBox()
        self.glade.get_widget("HBox3").add(self.boxes['gate'])
        
        self.boxes['comp'] = CompBox()
        self.glade.get_widget("HBox2").add(self.boxes['comp'])
        
        self.boxes['modbox'] = ModBox()
        self.glade.get_widget("ModBox").add(self.boxes['modbox'])
        self.boxes['modcombobox'] = ModComboBox()
        self.glade.get_widget("ModBox").add(self.boxes['modcombobox'])

        self.boxes['delaybox'] = DelayBox()
        self.glade.get_widget("DelayBox").add(self.boxes['delaybox'])
        self.boxes['delaycombobox'] = DelayComboBox()
        self.glade.get_widget("DelayBox").add(self.boxes['delaycombobox'])
        
        self.boxes['eqbox'] = EQBox()
        self.glade.get_widget("MainVBox").add(self.boxes['eqbox'])

        for e in self.boxes:
            self.boxes[e].show()

    def presets_changed(self, presets):
        if presets != None:
            for e in presets:
                self.boxes[e].changed()
        else:
            for e in self.boxes:
                self.boxes[e].changed()

        p = pod.Pod()
        self.presetid.set_text("%d%s" % (p.pid / 4 + 1, chr(p.pid % 4 + 65)))
        self.presetname.set_text(p.patches[p.pid].presetname)
        
        self.prev_channel.set_sensitive(p.pid > 0)
        self.next_channel.set_sensitive(p.pid < p.channel_number)
            
    def do_delete_event(self, widget, ev):
        pod.Pod().close()
        gtk.main_quit()

    def previous_channel_cb(self, obj):
        curid = pod.Pod().pid
        if curid > 0:
            pod.Pod().set_channel(curid - 1)

    def next_channel_cb(self, obj):
        curid = pod.Pod().pid
        if curid < pod.Pod().channel_number:
            pod.Pod().set_channel(curid + 1)

    def open_file_cb(self, obj):
        fd = gtk.FileSelection("File selection")
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

            pod.Pod().set_current_patch(buf)

    def open_l6t_file_cb(self, obj):
        i = ImportL6T("marshall-jcm800.l6t")
        i.parse()
        print i.buffer
