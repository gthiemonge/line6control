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

import pod
from controls import *

class ComboBox(Gtk.ComboBox):
    __gtype_name__ = 'ComboBox'

    def __init__(self):
        Gtk.ComboBox.__init__(self)

        self.from_device = False

        elem = Gtk.CellRendererText()
        self.pack_start(elem, True)
        self.add_attribute(elem, "text", 1)

        self.create_store()
        self.fill()

    def fill(self):
        for id in self.models:
            try:
                name = self.models[id].realname
                if name == '':
                    name = self.models[id].name
            except:
                name = self.models[id].name

            self.store.append([id, name])

    def create_store(self):
        self.store = Gtk.ListStore(int, str)
        self.set_model(self.store)

    def set_active(self, id, from_device = False):
        self.from_device = from_device

        iter = self.store.get_iter_first()
        i = 0

        while iter != None:
            if self.store.get(iter, 0)[0] == id:
                break
            iter = self.store.iter_next(iter)
            i += 1

        Gtk.ComboBox.set_active(self, i)

        self.from_device = False

    def do_changed(self):
        if self.get_active() != -1 and self.from_device == False:
            value = int(self.store.get(self.get_active_iter(), 0)[0])
            pod.Pod.get().send_cc(self.control, value)

            # Changing Amp auto-updates
            if self.__class__.__name__ != 'AmpComboBox':
                pod.Pod.get().get_current_patch()
                pod.Pod.get().update()

    def changed(self):
        try:
            val = pod.Pod.get().get_param(self.control)
            self.set_active(val, True)
        except Exception as e:
            print("can't change %s : %s" % (self.__gtype_name__, e))


class StompComboBox(ComboBox):
    __gtype_name__ = 'StompComboBox'

    control = STOMP_Model
    models = StompModels

class ModComboBox(ComboBox):
    __gtype_name__ = 'ModComboBox'

    control = MOD_Model
    models = ModModels

class DelayComboBox(ComboBox):
    __gtype_name__ = 'DelayComboBox'

    control = DELAY_Model
    models = DelayModels

class AmpComboBox(ComboBox):
    __gtype_name__ = 'AmpComboBox'

    control = 11 # ??
    models = AmpModels

    # specific for Amp !!
    def changed(self):
        try:
            self.set_active(pod.Pod.get().get_param(AMP_Model), True)
        except Exception as e:
            print("can't change ampcombobox : %s" % (e))

class CabComboBox(ComboBox):
    __gtype_name__ = 'CabComboBox'

    control = CAB_Model
    models = CabModels
