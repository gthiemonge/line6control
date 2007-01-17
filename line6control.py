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
    print "Cannont find podc.so, you need run 'make' to compile pypod.c."
    sys.exit()

import pygtk
pygtk.require('2.0')
import gtk

import pod
import ui

import gettext
from gettext import gettext as _
_ = gettext.gettext

if __name__ == '__main__':
    try:
        devices = pod.get_devices()
        pod.Pod(devices[0])
    except IndexError:
        dialog = gtk.MessageDialog(None, 0, gtk.MESSAGE_ERROR, gtk.BUTTONS_OK,
                                   _("Can't find Line 6 device.\nCheck your connection."))
        dialog.run()
        dialog.destroy()
        sys.exit(1)
        
    ui.Interface()
    gtk.main()

