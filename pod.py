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
#     def send_sysex(self, buffer)
#     def param_handler(self, param, value)
#     def program_handler(self, value)
#     def sysex_handler(self, buffer)

(
    ACTION_LIST_PATCHES,
    ACTION_NONE
    ) = range(2)

class PodDebug(podc.Pod):
    def __init__(self, card):
        super(PodDebug, self).__init__(card)

        self.midi_messages = []
        self.cur_sysex = None
        self.cur_replies = []

        self.sysex_cache = {}

        #try:
        #    with open('debug.dump') as fp:
        #        d = yaml.safe_load(fp.read())
        #        for msgs in d:
        #            request, replies = msgs
        #            self.sysex_cache[request] = replies
        #except Exception as e:
        #    print(e)

    def send_cc(self, param, value):
        super(PodDebug, self).send_cc(param, value)

    def send_pc(self, value):
        super(PodDebug, self).send_pc(value)

    def send_sysex(self, buffer):
        key = "".join("\\x{:02x}".format(b) for b in buffer)
        print("send_sysex(buffer={})".format(key))
        if key in self.sysex_cache:
            print("found in cache (reply={})".format(self.sysex_cache[key]))
            for reply in self.sysex_cache[key]:
                ret = [int(b[1:], 16) for b in reply.split('\\')[1:]]
                print(ret)
                self._sysex_handler(ret)
            return

        if self.cur_replies:
            self.midi_messages.append([self.cur_sysex, self.cur_replies])

        self.cur_sysex = key
        self.cur_replies = []
        super(PodDebug, self).send_sysex(buffer)

    def sysex_handler(self, buffer):
        key = "".join("\\x{:02x}".format(b) for b in buffer)
        print("sysex_handler(buffer={})".format(key))
        self.cur_replies.append(key)
        self._sysex_handler(buffer);

    def dump(self):
        if self.cur_replies:
            self.midi_messages.append([self.cur_sysex, self.cur_replies])

        if self.midi_messages:
            with open('debug.dump', 'w') as fp:
                fp.write(yaml.dump(self.midi_messages))

class Pod(PodDebug):
    __instance = None

    channel_number = 127

    @classmethod
    def get(cls):
        return cls.__instance

    def __init__(self, card=None):
        super(Pod, self).__init__(card)

        Pod.__instance = self

        self.patches = {}
        self.pid = 0

        self.firmware_version = 0

        self.action = ACTION_NONE

        self.get_firmware_version()
        GObject.idle_add(self.list_patches)

    def update(self, presets = None):
        print("update(presets={})".format(presets))
        GObject.idle_add(Interface.get().presets_changed, presets)

    def set_buffer(self, buffer):
        sysex = buffer
        sysex[0:7] = [0xF0, 0x00, 0x01, 0x0C, 0x03, 0x74, 0x05]

        #print sysex

    def get_firmware_version(self):
        self.send_sysex((0xF0, 0x7E, 0x7F, 0x06,
                         0x01, 0xF7))

    def get_current_patch(self):
        self.send_sysex((0xF0, 0x00, 0x01, 0x0C,
                         0x03, 0x75, 0xF7))
        self.update()

    def get_patch(self, id):
        self.send_sysex((0xF0, 0x00, 0x01, 0x0C,
                         0x03, 0x73, (id > 0x3F) and 1 or 0, id,
                         0x00, 0x00, 0xF7))

    def set_current_patch(self, buf):
        sysex = [0xF0, 0x00, 0x01, 0x0C,
                 0x03, 0x74, 0x05]
        sysex += map(ord, buf)
        sysex.append(0xF7)

        self.send_sysex(sysex)
        self.update()

    def send_cc(self, param, value):
        debug_msg("send_cc(%d, %d)" % (param, value))
        self.patches[self.pid].set_value(param, value)
        podc.Pod.send_cc(self, param, value)

    def set_channel(self, channel):
        self.pid = channel
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
        self.pid = value
        self.update()

    def _sysex_handler(self, buffer):
        debug_msg("dump 0x%x" % (buffer[5]))

        if buffer[0:5] == [0xF2, 0x7E, 0x7F, 0x06, 0x02]:
            self.firmware_version = buffer[13] * 100 + buffer[14] * 10 + buffer[15];
            debug_msg("firmware version %d" % (self.firmware_version))
        if buffer[5] == 0x72: # finish dump
            if self.action == ACTION_LIST_PATCHES:
                debug_msg("Retrieving `%s'." % (self.patches[self.pid].presetname))

                if self.pid < self.channel_number:
                    # retrieve next patch
                    self.list_patches(self.pid + 1, False)
                elif self.pid == self.channel_number:
                    # all patch done
                    self.action = ACTION_NONE
                    GObject.idle_add(self.get_current_patch)

                    self.dump()
        if buffer[5] == 0x74: #dump
            if self.action == ACTION_LIST_PATCHES:
                # store patch in list
                self.patches[self.pid] = Preset()
                self.patches[self.pid].import_buffer(buffer)
            else:
                # update patch in list
                self.patches[self.pid].import_buffer(buffer)
                self.update()

    def list_patches(self, pid = 0, first = True):
        self.action = ACTION_LIST_PATCHES

        print("list_patches(pid={}, first={})".format(pid, first))
        # wait for last patch in self.patch
        if not self.pid in self.patches and first == False:
            return True

        self.pid = pid
        self.send_sysex((0xF0, 0x00, 0x01, 0x0C,
                         0x03, 0x73, (pid > 0x3F), pid,
                         0x00, 0x00, 0xF7))

        return False

    def get_param(self, param):
        return self.patches[self.pid].get_value(param)

import re

def get_devices():
    devices = []

    f = open("/proc/asound/cards")

    reg = re.compile('\s*(\d+) \[PODxt')

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
