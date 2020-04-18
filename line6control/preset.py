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
        self.presetname = ''

        self.params = {}

    def import_params(self, name, params):
        self.presetname = name
        self.params = params

    def __repr__(self):
        return "<%s(`%s')>" % (self.__class__.__name__, self.presetname)

    def get_value(self, param):
        if param not in self.params:
            print("FIXME unknown param {}".format(param))
            return 0
        return self.params[param]

    def set_value(self, param, val):
        self.params[param] = val
