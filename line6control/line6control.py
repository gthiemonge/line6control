#!/usr/bin/env python
#  Line 6 Control - an application for Line 6 USB devices
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

import sys

try:
    import podc
except:
    print("Cannont find podc.so, you need run 'make' to compile pypod.c.")
    sys.exit()

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

import line6control.pod
import line6control.ui


def main():
    try:
        devices = line6control.pod.get_devices()
        line6control.pod.Pod(devices[0])
    except IndexError:
        dialog = Gtk.MessageDialog(None, 0, Gtk.MessageType.ERROR,
                                   Gtk.ButtonsType.OK,
                                   "Can't find Line 6 device.\nCheck your connection.")
        dialog.run()
        dialog.destroy()
        sys.exit(1)

    line6control.ui.Interface()
    Gtk.main()


if __name__ == '__main__':
    main()
