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

Preset_Name = slice(7, 23)

class Preset(object):
    def __init__(self):
        self.buffer = None

    def import_buffer(self, buffer):
        self.presetname = "".join(map(chr, buffer[Preset_Name])).strip('\x00')
        self.buffer = buffer

    def __repr__(self):
        return "<%s(`%s', %s)>" % (self.__class__.__name__, self.presetname)

    def get_value(self, param):
        return self.buffer[0x27 + param]

    def set_value(self, param, val):
        self.buffer[0x27 + param] = val
