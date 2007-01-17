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
import gtk.gdk
import pango
import cairo

import math
import time
import sys

from controls import *
import pod
from resources import Resources

class Box(gtk.DrawingArea):
    __gtype_name__ = 'Box'
    
    control = None
    pressed_knob = None
    button_y = 0

    box_name = 'Box'

    last_button_press_event = 0

    last_sent = None

    def __init__(self):
        gtk.DrawingArea.__init__(self)

        self.add_events(gtk.gdk.EXPOSURE_MASK |
                        gtk.gdk.BUTTON_PRESS_MASK |
                        gtk.gdk.BUTTON_RELEASE_MASK |
                        gtk.gdk.POINTER_MOTION_MASK)

        self.set_size_request(self.width, self.height)
        
    def do_button_press_event(self, ev):
        if ev.button == 1:
            t = time.time()
            if t - self.last_button_press_event < 0.1: # double click
                self.toggle_enabled()

            self.last_button_press_event = t
            
            x = 35
            i = 0
            id = None
            xd = Resources().knob_background.get_width()
            
            while x < self.width:
                if ev.x >= x and ev.x <= x + xd:
                    id = i
                    break
                x += self.xdiff
                i += 1

            try:
                curr = self.control.controls[id]
            except:
                curr = None

            if curr != None:
                if curr[0] == MOD_PrePost or curr[0] == DELAY_PrePost:
                    value = pod.Pod().get_boolean_param(curr.control_id)
                    pod.Pod().set_boolean_param(curr.control_id, not value)
                    self.queue_draw()
                else:                
                    self.pressed_knob = curr
                    self.button_y = ev.y

    def do_button_release_event(self, ev):
        if ev.button == 1:
            self.pressed_knob = None

    def do_motion_notify_event(self, ev):
        if self.pressed_knob != None:
            value = pod.Pod().get_param(self.pressed_knob[0])
            value += int(self.button_y - ev.y)

            if value < self.pressed_knob.device_range[0]:
                value = self.pressed_knob.device_range[0]
            if value > self.pressed_knob.device_range[1]:
                value = self.pressed_knob.device_range[1]

            now = time.time ()
            if self.last_sent == None or (now - self.last_sent) > 0.01:
                pod.Pod().send_cc(self.pressed_knob.control_id, value)
                self.last_sent = now

            self.button_y = ev.y
            self.queue_draw()

    def do_expose_event(self, ev):
        self.ctx = self.window.cairo_create()

        # draw background
        if self.is_enabled():
            offset = 10
            radius = 9
            self.ctx.arc(offset, offset, radius,
                    - math.pi, - math.pi / 2)
            self.ctx.arc(self.width - offset, offset, radius,
                    - math.pi / 2, 0)
            self.ctx.arc(self.width - offset, self.height - offset, radius,
                    0, math.pi / 2)
            self.ctx.arc(offset, self.height - offset, radius,
                    math.pi / 2, math.pi)
            self.ctx.set_source_rgb(.7, .8, .9)
            self.ctx.fill()
        else:
            color = self.style.bg_gc[0]
            self.window.draw_rectangle(color, True,
                                       ev.area.x, ev.area.y,
                                       ev.area.width, ev.area.height)

        self.show_title()

        if self.control == None:
            return False

        # FIXME: add cab box controls
        if self.control.controls == None:
            return False
        
        k_pix = Resources().knob_pix
        k_bg_pix = Resources().knob_background

        xoffset = 35
        yoffset = (self.height - k_bg_pix.get_height()) / 2

        for elem in self.control.controls:
            if elem.control_id == MOD_PrePost or elem.control_id == DELAY_PrePost:
                value = pod.Pod().get_boolean_param(elem.control_id)
                self.show_text_boolean('PRE', 'POST', value, xoffset, yoffset)

                if value == False:
                    xk = 40
                else:
                    xk = 0

                sw = Resources().switch
                self.window.draw_pixbuf(self.style.black_gc, sw,
                                        xk, 0,
                                        xoffset, yoffset,
                                        k_bg_pix.get_width(), k_bg_pix.get_height())
            else:
                value = float(pod.Pod().get_param(elem.control_id))
                str = elem.name
                
                self.window.draw_pixbuf(self.style.black_gc,
                                        k_bg_pix,
                                        0, 0,
                                        xoffset, yoffset,
                                        k_bg_pix.get_width(), k_bg_pix.get_height())
            
                offset = (int)(1920.0 * value / 127.0);
                xk = offset % 160;
                xk = 120 - (xk - (xk % 40));
                yk = offset / 160;
                yk = yk * 40;
                if xk == 120 and yk == 480:
                    xk = 0
                    yk = 440

                self.window.draw_pixbuf(self.style.black_gc,
                                        k_pix,
                                        xk, yk,
                                        xoffset, yoffset,
                                        k_bg_pix.get_width(), k_bg_pix.get_height())
                
                self.show_text(elem, value, xoffset, yoffset)

            xoffset += self.xdiff

        return False

    def show_text(self, elem, value, x, y):
        
        k_pix = Resources().knob_pix
        k_bg_pix = Resources().knob_background
        
        self.ctx = self.window.cairo_create()

        try:
            rr = elem.phys_range
            try:
                mr = elem.device_range

                if value > mr[1]:
                    value = mr[1]
                if value < mr[0]:
                    value = mr[0]
                
                r = (value - mr[0]) / (mr[1] - mr[0])
                v = round((rr[1] - rr[0]) * r + rr[0])
            except:
                v = (rr[1] - rr[0]) * value + rr[0]
                v = round(v / 127.0)
                
            str = "%d" % (v)
            
            try:
                str += " %s" % (rr[2])
            except:
                pass
        except:
            str = "%d %%" % (value / 1.27)
            
        self.ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL,
                             cairo.FONT_WEIGHT_BOLD)
        if self.is_enabled():
            self.ctx.set_source_rgb(.2, .2, .2)
        else:
            self.ctx.set_source_rgb(.4, .4, .4)
        self.ctx.set_font_size(10)
        
        self.ctx.new_path()
        width, height = self.ctx.text_extents(str)[2:4]
        self.ctx.move_to(int(x + k_bg_pix.get_width() / 2 - width / 2),
                    int(self.height - 5 - height))
        self.ctx.text_path(str)
        self.ctx.fill()

        self.ctx.new_path()
        width, height = self.ctx.text_extents(elem.name)[2:4]
        self.ctx.move_to(int(x + k_bg_pix.get_width() / 2 - width / 2),
                    int(y - 5))
        self.ctx.text_path(elem.name)
        self.ctx.fill()

    def show_text_boolean(self, text1, text2, value, x, y):
        k_pix = Resources().knob_pix
        k_bg_pix = Resources().knob_background

        self.ctx = self.window.cairo_create()

        self.ctx.set_antialias(cairo.ANTIALIAS_SUBPIXEL)
            
        self.ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL,
                             cairo.FONT_WEIGHT_BOLD)
        if self.is_enabled():
            self.ctx.set_source_rgb(.2, .2, .2)
        else:
            self.ctx.set_source_rgb(.4, .4, .4)
        self.ctx.set_font_size(10)

        self.ctx.new_path()
        width, height = self.ctx.text_extents(text1)[2:4]
        self.ctx.move_to(int(x + k_bg_pix.get_width() / 2 - width / 2),
                    int(self.height - 5 - height))
        self.ctx.text_path(text1)
        self.ctx.fill()

        self.ctx.new_path()
        width, height = self.ctx.text_extents(text2)[2:4]
        self.ctx.move_to(int(x + k_bg_pix.get_width() / 2 - width / 2),
                    int(y - 5))
        self.ctx.text_path(text2)
        self.ctx.fill()

    def show_title(self):
        if self.is_enabled():
            self.ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
            self.ctx.set_source_rgb(.3, .4, .5)
        else:
            self.ctx.select_font_face("Sans")
            self.ctx.set_source_rgb(.6, .6, .6)
        self.ctx.set_font_size(9)

        self.ctx.new_path()
        width, height = self.ctx.text_extents(self.box_name)[2:4]
        self.ctx.move_to(15, int((self.height + width) / 2))
        self.ctx.rotate(- math.pi / 2)
        self.ctx.text_path(self.box_name)
        self.ctx.fill()
        
    def changed(self):
        try:
            self.control = self.model[pod.Pod().get_param(self.control_model)]
            self.queue_draw()
        except Exception, e:
            print "can't change box : %s" % (sys.exc_info()[0])
            self.control = None

    def is_enabled(self):
        return pod.Pod().get_boolean_param(self.control_enable)
    
    def toggle_enabled(self):
        pod.Pod().set_boolean_param(self.control_enable, not self.is_enabled())
        self.queue_draw()


class AmpBox(Box):
    __gtype_name__ = 'AmpBox'

    model = AmpModels
    control_model = AMP_Model
    control_enable = AMP_Enable

    box_name = 'Amps'
    
    width = 400
    height = 90
    xdiff = 60
    
    def is_enabled(self):
        return not pod.Pod().get_boolean_param(self.control_enable)

    def toggle_enabled(self):
        pod.Pod().set_boolean_param(self.control_enable, self.is_enabled())
        self.queue_draw()

class CabBox(Box):
    __gtype_name__ = 'CabBox'

    model = CabModels
    control_model = CAB_Model
    control_enable = None

    box_name = 'Cab'

    width = 150
    height = 90
    xdiff = 60

    def is_enabled(self):
        if pod.Pod().get_param(self.control_model) == 0:
            return False
        else:
            return True

    def toggle_enabled(self):
        pass

class StompBox(Box):
    __gtype_name__ = 'StompBox'

    model = StompModels
    control_model = STOMP_Model
    control_enable = STOMP_Enable

    box_name = 'Stomp'

    width = 400
    height = 90
    xdiff = 50

class ModBox(Box):
    __gtype_name__ = 'ModBox'

    model = ModModels
    control_model = MOD_Model
    control_enable = MOD_Enable

    box_name = 'Mod'

    width = 400
    height = 90
    xdiff = 50

class DelayBox(Box):
    __gtype_name__ = 'DelayBox'

    model = DelayModels
    control_model = DELAY_Model
    control_enable = DELAY_Enable

    box_name = 'Delay'

    width = 400
    height = 90
    xdiff = 50

class CompBox(Box):
    __gtype_name__ = 'CompBox'

    model = CompModels
    control_model = None
    control_enable = COMP_Enable
    control = CompModels[0]

    box_name = 'Comp'
    
    width = 150
    height = 90
    xdiff = 50

    def changed(self):
        self.queue_draw()

class NoiseGateBox(Box):
    __gtype_name__ = 'NoiseGateBox'

    model = NoiseGateModels
    control_model = None
    control_enable = GATE_Enable
    control = NoiseGateModels[0]

    box_name = 'Gate'

    width = 150
    height = 90
    xdiff = 50
    
    def changed(self):
        self.queue_draw()
        
