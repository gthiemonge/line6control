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

import line6control.pod
import podc
from line6control.controls import *

class ComboBox(Gtk.ComboBox):
    __gtype_name__ = 'ComboBox'

    def __init__(self, device):
        Gtk.ComboBox.__init__(self)

        self.models = self.base_models.get(device)

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
            line6control.pod.Pod.get().send_cc(self.control, value)

            # Changing Amp auto-updates
            if self.__class__.__name__ != 'AmpComboBox':
                line6control.pod.Pod.get().get_current_patch()
                line6control.pod.Pod.get().update()

    def changed(self):
        if len(self.models) == 1:
            return
        p = line6control.pod.Pod.get()
        param = p.get_param(self.control)
        self.set_active(param, True)

class EffectComboBox(ComboBox):
    __gtype_name__ = 'EffectComboBox'

    control = EFFECT_Setup
    base_models = EffectModels

class StompComboBox(ComboBox):
    __gtype_name__ = 'StompComboBox'

    control = STOMP_Model
    base_models = StompModels

class ModComboBox(ComboBox):
    __gtype_name__ = 'ModComboBox'

    control = MOD_Model
    base_models = ModModels

class DelayComboBox(ComboBox):
    __gtype_name__ = 'DelayComboBox'

    control = DELAY_Model
    base_models = DelayModels

class AmpComboBox(ComboBox):
    __gtype_name__ = 'AmpComboBox'

    base_models = AmpModels

    def __init__(self, device):
        if device == podc.DEVICE_POCKETPOD:
            self.control = 12
        else:
            self.control = 11

        super(AmpComboBox, self).__init__(device)

    # specific for Amp !!
    def changed(self):
        p = line6control.pod.Pod.get()
        #if p.device == podc.DEVICE_POCKETPOD:
        param = p.get_param(AMP_Model_wo_defaults)
        #else:
        #    param = p.get_param(AMP_Model)
        self.set_active(param, True)

class CabComboBox(ComboBox):
    __gtype_name__ = 'CabComboBox'

    control = CAB_Model
    base_models = CabModels

class MicComboBox(ComboBox):
    __gtype_name__ = 'MixComboBox'

    control = MIC_Select
    base_models = MicModels

class ReverbComboBox(ComboBox):
    __gtype_name__ = 'ReverbComboBox'

    control = REVERB_Model
    base_models = ReverbModels
