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

(
    COLUMN_ID,
    COLUMN_PODID,
    COLUMN_NAME
    ) = range(3)

class PresetList(Gtk.TreeView):
    __gtype_name__ = 'PresetList'

    def __init__(self):
        Gtk.TreeView.__init__(self)

        self.set_headers_visible(False)

        self.create_model()
        self.set_model(self.model)

        self.add_columns()

        self.set_size_request(150, -1)

        for i in pod.Pod.get().patches:
            patch = pod.Pod.get().patches[i]

            podid = "%d%s" % (i / 4 + 1, chr(i % 4 + 65))
            name = patch.presetname

            self.add_elem(i, podid, name)

    def create_model(self):
        self.model = Gtk.ListStore(GObject.TYPE_UINT,
                               GObject.TYPE_STRING,
                               GObject.TYPE_STRING)

    def add_columns(self):
        column = Gtk.TreeViewColumn('podid', Gtk.CellRendererText(),
                                    text=COLUMN_PODID)
        self.append_column(column)

        column = Gtk.TreeViewColumn('name', Gtk.CellRendererText(),
                                    text=COLUMN_NAME)
        self.append_column(column)

    def add_elem(self, id, podid, name):
        iter = self.model.append()
        self.model.set(iter,
                       COLUMN_ID, id,
                       COLUMN_PODID, podid,
                       COLUMN_NAME, name)

    def do_row_activated(self, path, view):
        iter = self.model.get_iter(path)
        id = self.model.get_value(iter, COLUMN_ID)
        pod.Pod.get().set_channel(id)
