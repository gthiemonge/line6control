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
import gobject

import pod
from controls import *

class ComboBox(gtk.ComboBox):
    __gtype_name__ = 'ComboBox'

    def __init__(self):
        gtk.ComboBox.__init__(self)

        self.from_device = False
        
        self.create_store()

        elem = gtk.CellRendererText()
        self.pack_start(elem)

        self.set_attributes(elem, text=1)

        self.fill()

    def fill(self):
        for id in self.models:
            iter = self.store.append()
            try:
                name = self.models[id].realname
                if name == '':
                    name = self.models[id].name
            except:
                name = self.models[id].name
            self.store.set(iter, 0, id, 1, name)
                
            
    def create_store(self):
        self.store = gtk.ListStore(gobject.TYPE_UINT,
                                   gobject.TYPE_STRING)

        self.set_model(self.store)

    def set_active(self, id, from_device = False):
        self.from_device = from_device

        iter = self.store.get_iter_root()
        i = 0
        
        while iter != None:
            if self.store.get(iter, 0)[0] == id:
                break
            iter = self.store.iter_next(iter)
            i += 1

        gtk.ComboBox.set_active(self, i)

        self.from_device = False

    def do_changed(self):
        if self.get_active() != -1 and self.from_device == False:
            value = int(self.store.get(self.get_active_iter(), 0)[0])
            pod.Pod().send_cc(self.control, value)

            # Changing Amp auto-updates
            if self.__class__.__name__ != 'AmpComboBox':
                pod.Pod().get_current_patch()
                pod.Pod().update()

    def changed(self):
        try:
            val = pod.Pod().get_param(self.control)
            self.set_active(val, True)
        except Exception, e:
            print "can't change %s : %s" % (self.__gtype_name__, e)


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
            self.set_active(pod.Pod().get_param(AMP_Model), True)
        except Exception, e:
            print "can't change ampcombobox : %s" % (e)

class CabComboBox(ComboBox):
    __gtype_name__ = 'CabComboBox'

    control = CAB_Model
    models = CabModels
    
