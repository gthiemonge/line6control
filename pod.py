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

import re
import yaml

import podc

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gi.repository import GObject

from preset import Preset
from controls import *

from ui import Interface
from utils import debug_msg

# defined in podc
#
# class Pod:
#     def __init__(self, card)
#     def close(self)
#     def send_cc(self, param, value)
#     def send_pc(self, value)
#     def param_handler(self, param, value)
#     def program_handler(self, value)

class Pod(podc.Pod):
    __instance = None

    @classmethod
    def get(cls):
        return cls.__instance

    def __init__(self, card=None):
        super(Pod, self).__init__(card)

        Pod.__instance = self

        self.patches = {}
        self.pid = 0

    def run(self):
        print(self.device, self.firmware_version)

    def update(self, presets=None):
        GObject.idle_add(Interface.get().presets_changed, presets)

    def on_current_patch(self):
        self.update()

    def send_cc(self, param, value):
        debug_msg("send_cc(%d, %d)" % (param, value))
        self.patches[self.pid].set_value(param, value)
        podc.Pod.send_cc(self, param, value)

    def set_channel(self, channel):
        debug_msg("send_pc({})".format(channel))
        self.pid = channel
        if self.device == podc.DEVICE_POCKETPOD:
            self.send_pc(channel + 1)
            print(self.patches[self.pid])
            print(self.patches[self.pid].params)
            self.update()
        else:
            self.send_pc(channel)

    def set_boolean_param(self, param, value):
        if value == False: value = 0
        else:              value = 127

        self.patches[self.pid].set_value(param, value)
        self.send_cc(param, value)

    def get_boolean_param(self, param):
        val = self.patches[self.pid].get_value(param)
        if val < 64:       return False
        else:              return True

    def param_handler(self, param, value):
        debug_msg("param(%d, %d)" % (param, value))
        self.patches[self.pid].set_value(param, value)

        # if we change an effect, we need to get all parameters values
        if param in (STOMP_Model, MOD_Model, DELAY_Model):
            self.get_current_patch()
        elif not param in (STOMP_Model, AMP_Model, MOD_Model, DELAY_Model):
            p = None

            if param in (AMP_Drive, AMP_Bass, AMP_Mid,
                         AMP_Treble, AMP_Presence, AMP_ChanVol, AMP_Pan):
                p = ['ampbox']

            if param in (COMP_Gain, COMP_Thresh, COMP_Enable):
                p = ['comp']

            if param in (GATE_Thresh, GATE_Decay, GATE_Enable):
                p = ['gate']

            if param == STOMP_Model:
                p = ['stompbox']

            if param in (STOMP_Param1, STOMP_Param1_NoteValue, STOMP_Param2,
                         STOMP_Param3, STOMP_Param4, STOMP_Param5,
                         STOMP_VolumeMix, STOMP_Enable):
                p = ['stompbox']

            if param == MOD_Model:
                p = ['modbox']

            if param in (MOD_Param1, MOD_Param1_DoublePrec, MOD_Param1_NoteValue,
                         MOD_Param2, MOD_Param3, MOD_Param4, MOD_Param5,
                         MOD_VolumeMix, MOD_PrePost, MOD_Enable):
                p = ['modbox']

            if param == DELAY_Model:
                p = ['delaybox']

            if param in (DELAY_Param1, DELAY_Param1_DoublePrec, DELAY_Param1_NoteValue,
                         DELAY_Param2, DELAY_Param3, DELAY_Param4, DELAY_Param5,
                         DELAY_VolumeMix, DELAY_PrePost, DELAY_Enable):
                p = ['delaybox']

            self.update(p)

    def program_handler(self, value):
        debug_msg("program changed to %d" % (value))
        if self.device == podc.DEVICE_POCKETPOD:
            self.pid = value - 1
        else:
            self.pid = value
        self.update()

    def on_patch_update(self, pid, name, params):
        print("on_patch_update(pid={}, name={}, params={})".format(pid, name, params))
        self.patches[pid] = Preset()
        self.patches[pid].import_params(name, params)

    def get_param(self, param):
        return self.patches[self.pid].get_value(param)

def get_devices():
    devices = []

    f = open("/proc/asound/cards")

    reg = re.compile('\s*(\d+) \[POD') #XXX

    while True:
        l = f.readline()
        if l == '':
            break
        m = reg.match(l)
        if m != None:
            print("ok")
            devices.append(int(m.group(1)))
    f.close()

    print(devices)

    return devices
