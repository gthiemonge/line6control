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
from gi.repository import Gdk
import cairo

import math
import time
import sys

from line6control.controls import *
import line6control.pod
import podc
from .resources import Resources

class Box(Gtk.DrawingArea):
    __gtype_name__ = 'Box'

    base_model = None
    control = None
    has_control = False
    pressed_knob = None
    button_y = 0

    box_name = 'Box'

    last_button_press_event = 0

    last_sent = None

    def __init__(self, device):
        Gtk.DrawingArea.__init__(self)

        self.model = self.base_model.get(device)
        if self.has_control:
            self.control = self.model[0]

        self.add_events(Gdk.EventMask.EXPOSURE_MASK |
                        Gdk.EventMask.BUTTON_PRESS_MASK |
                        Gdk.EventMask.BUTTON_RELEASE_MASK |
                        Gdk.EventMask.POINTER_MOTION_MASK)

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
            xd = Resources.get().knob_background.get_width()

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
                if curr.control_id in (MOD_PrePost, DELAY_PrePost, REVERB_PrePost):
                    value = line6control.pod.Pod.get().get_boolean_param(curr.control_id)
                    line6control.pod.Pod.get().set_boolean_param(curr.control_id, not value)
                    self.queue_draw()
                else:
                    self.pressed_knob = curr
                    self.button_y = ev.y

    def do_button_release_event(self, ev):
        if ev.button == 1:
            self.pressed_knob = None

    def do_motion_notify_event(self, ev):
        if self.pressed_knob != None:
            value = line6control.pod.Pod.get().get_param(self.pressed_knob.control_id)
            value += int(self.button_y - ev.y)

            if value < self.pressed_knob.device_range[0]:
                value = self.pressed_knob.device_range[0]
            if value > self.pressed_knob.device_range[1]:
                value = self.pressed_knob.device_range[1]

            now = time.time ()
            if self.last_sent == None or (now - self.last_sent) > 0.01:
                line6control.pod.Pod.get().send_cc(self.pressed_knob.control_id, value)
                self.last_sent = now

            self.button_y = ev.y
            self.queue_draw()


    def do_draw(self, ct):
        self.do_expose_event(ct)

    def do_expose_event(self, ctx):
        self.ctx = ctx #self.window.cairo_create()

        target = ctx.get_target()
        overlay = target.create_similar(cairo.CONTENT_COLOR_ALPHA,
                                        self.width, self.height)
        knobs = target.create_similar(cairo.CONTENT_COLOR_ALPHA,
                                        self.width, self.height)

        overlay_cr = cairo.Context(overlay)

        # draw background
        if self.is_enabled():
            offset = 10
            radius = 9
            overlay_cr.arc(offset, offset, radius,
                    - math.pi, - math.pi / 2)
            overlay_cr.arc(self.width - offset, offset, radius,
                    - math.pi / 2, 0)
            overlay_cr.arc(self.width - offset, self.height - offset, radius,
                    0, math.pi / 2)
            overlay_cr.arc(offset, self.height - offset, radius,
                    math.pi / 2, math.pi)
            overlay_cr.set_source_rgb(.7, .8, .9)
            overlay_cr.fill()
        else:
            pass
            #color = self.get_style().bg_gc[0]
            #self.window.draw_rectangle(color, True,
            #                           0, 0,
            #                           self.get_allocation().width,
            #                           self.get_allocation().heigh)
            #                           #ev.area.x, ev.area.y,
            #                           #ev.area.width, ev.area.height)


        if self.control == None:
            return False

        # FIXME: add cab box controls
        if self.control.controls == None:
            return False

        knobs_cr = cairo.Context(knobs)

        k_pix = Resources.get().knob_pix
        k_bg_pix = Resources.get().knob_background

        xoffset = 35
        yoffset = (self.height - k_bg_pix.get_height()) / 2

        p = line6control.pod.Pod.get()

        for elem in self.control.controls:
            if elem.control_id in (MOD_PrePost, DELAY_PrePost, REVERB_PrePost):
                value = line6control.pod.Pod.get().get_boolean_param(elem.control_id)
                self.show_text_boolean(overlay_cr,
                                       'PRE', 'POST', value, xoffset, yoffset)

                if value == False:
                    xk = 40
                else:
                    xk = 0

                knob_fg = knobs.create_similar(cairo.CONTENT_COLOR_ALPHA, 40, 40)
                knob_fg_cr = cairo.Context(knob_fg)

                sw = Resources.get().switch
                knob_fg_cr.set_source_surface(sw, -xk, 0)
                knob_fg_cr.paint()

                knobs_cr.set_source_surface(knob_fg, xoffset, yoffset)
                knobs_cr.paint()
            else:
                value = float(p.get_param(elem.control_id))
                str = elem.name

                knobs_cr.set_source_surface(k_bg_pix, xoffset, yoffset)
                knobs_cr.paint()

                offset = (int)(1920.0 * value / 127.0);
                xk = offset % 160;
                xk = 120 - (xk - (xk % 40));
                yk = offset // 160;
                yk = yk * 40;
                if xk == 120 and yk == 480:
                    xk = 0
                    yk = 440

                knob_fg = knobs.create_similar(cairo.CONTENT_COLOR_ALPHA, 40, 40)
                knob_fg_cr = cairo.Context(knob_fg)

                knob_fg_cr.set_source_surface(k_pix, -xk, -yk)
                knob_fg_cr.paint()

                knobs_cr.set_source_surface(knob_fg, xoffset, yoffset)
                knobs_cr.paint()

                self.show_text(overlay_cr, elem, value, xoffset, yoffset)

            xoffset += self.xdiff


        overlay_cr.set_source_surface(knobs, 0, 0)
        overlay_cr.paint()

        self.show_title(overlay_cr)

        ctx.set_source_surface(overlay, 0, 0)
        ctx.paint()
        return False

    def show_text(self, ctx, elem, value, x, y):

        k_pix = Resources.get().knob_pix
        k_bg_pix = Resources.get().knob_background

        #self.ctx = self.window.cairo_create()

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

        ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL,
                             cairo.FONT_WEIGHT_BOLD)
        if self.is_enabled():
            ctx.set_source_rgb(.2, .2, .2)
        else:
            ctx.set_source_rgb(.4, .4, .4)
        ctx.set_font_size(10)

        ctx.new_path()
        width, height = ctx.text_extents(str)[2:4]
        ctx.move_to(int(x + k_bg_pix.get_width() / 2 - width / 2),
                    int(self.height - 5 - height))
        ctx.text_path(str)
        ctx.fill()

        ctx.new_path()
        width, height = ctx.text_extents(elem.name)[2:4]
        ctx.move_to(int(x + k_bg_pix.get_width() / 2 - width / 2),
                    int(y - 5))
        ctx.text_path(elem.name)
        ctx.fill()

    def show_text_boolean(self, ctx, text1, text2, value, x, y):
        k_pix = Resources.get().knob_pix
        k_bg_pix = Resources.get().knob_background

        ctx.set_antialias(cairo.ANTIALIAS_SUBPIXEL)

        ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL,
                             cairo.FONT_WEIGHT_BOLD)
        if self.is_enabled():
            ctx.set_source_rgb(.2, .2, .2)
        else:
            ctx.set_source_rgb(.4, .4, .4)
        ctx.set_font_size(10)

        ctx.new_path()
        width, height = ctx.text_extents(text1)[2:4]
        ctx.move_to(int(x + k_bg_pix.get_width() / 2 - width / 2),
                    int(self.height - 5 - height))
        ctx.text_path(text1)
        ctx.fill()

        ctx.new_path()
        width, height = ctx.text_extents(text2)[2:4]
        ctx.move_to(int(x + k_bg_pix.get_width() / 2 - width / 2),
                    int(y - 5))
        ctx.text_path(text2)
        ctx.fill()

    def show_title(self, ctx):
        if self.is_enabled():
            ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
            ctx.set_source_rgb(.3, .4, .5)
        else:
            ctx.select_font_face("Sans")
            ctx.set_source_rgb(.6, .6, .6)
        ctx.set_font_size(9)

        ctx.new_path()
        width, height = ctx.text_extents(self.box_name)[2:4]
        ctx.move_to(15, int((self.height + width) / 2))
        ctx.rotate(- math.pi / 2)
        ctx.text_path(self.box_name)
        ctx.fill()

    def changed(self):
        if len(self.model) == 1:
            self.control = self.model[0]
            self.queue_draw()
            return

        p = line6control.pod.Pod.get()
        param = p.get_param(self.control_model)
        self.control = self.model.get(param, self.model[0]) # XXX
        self.queue_draw()

    def is_enabled(self):
        return line6control.pod.Pod.get().get_boolean_param(self.control_enable)

    def toggle_enabled(self):
        line6control.pod.Pod.get().set_boolean_param(self.control_enable, not self.is_enabled())
        self.queue_draw()


class AmpBox(Box):
    __gtype_name__ = 'AmpBox'

    base_model = AmpModels
    control_model = AMP_Model
    control_enable = AMP_Enable

    box_name = 'Amps'

    width = 450
    height = 90
    xdiff = 60

    def __init__(self, device):
        p = line6control.pod.Pod.get()
        if p.device == podc.DEVICE_POCKETPOD:
            self.control_model = AMP_Model_wo_defaults

        super(AmpBox, self).__init__(device)

    def is_enabled(self):
        p = line6control.pod.Pod.get()
        if p.device == podc.DEVICE_POCKETPOD:
            return True
        return not p.get_boolean_param(self.control_enable)

    def toggle_enabled(self):
        line6control.pod.Pod.get().set_boolean_param(self.control_enable, self.is_enabled())
        self.queue_draw()

class CabBox(Box):
    __gtype_name__ = 'CabBox'

    base_model = CabModels
    control_model = CAB_Model
    control_enable = None

    box_name = 'Cab'

    width = 150
    height = 90
    xdiff = 60

    def is_enabled(self):
        p = line6control.pod.Pod.get()
        if p.device == podc.DEVICE_POCKETPOD:
            return line6control.pod.Pod.get().get_param(self.control_model) != 15  # XXX
        else:
            return line6control.pod.Pod.get().get_param(self.control_model) != 0

    def toggle_enabled(self):
        pass

class MicBox(Box):
    __gtype_name__ = 'MicBox'

    base_model = MicModels
    control_model = MIC_Select
    control_enable = None
    has_control = True

    box_name = 'Mic'

    width = 150
    height = 90
    xdiff = 60

    def is_enabled(self):
        return line6control.pod.Pod.get().get_param(ROOM_Level) > 0

    def toggle_enabled(self):
        pass

class StompBox(Box):
    __gtype_name__ = 'StompBox'

    base_model = StompModels
    control_model = STOMP_Model
    control_enable = STOMP_Enable

    box_name = 'Stomp'

    width = 450
    height = 90
    xdiff = 50

class EffectBox(Box):
    __gtype_name__ = 'EffectBox'

    base_model = EffectModels
    control_model = EFFECT_Setup
    control_enable = None

    box_name = 'Effect'

    width = 450
    height = 90
    xdiff = 50

    def is_enabled(self):
        return line6control.pod.Pod.get().get_param(TWEAK) > 0

class ModBox(Box):
    __gtype_name__ = 'ModBox'

    base_model = ModModels
    control_model = MOD_Model
    control_enable = MOD_Enable

    box_name = 'Mod'

    width = 450
    height = 90
    xdiff = 50

class DelayBox(Box):
    __gtype_name__ = 'DelayBox'

    base_model = DelayModels
    control_model = DELAY_Model
    control_enable = DELAY_Enable

    box_name = 'Delay'

    width = 450
    height = 90
    xdiff = 50

class CompBox(Box):
    __gtype_name__ = 'CompBox'

    base_model = CompModels
    control_model = None
    control_enable = COMP_Enable
    has_control = True

    box_name = 'Comp'

    width = 150
    height = 90
    xdiff = 50

    def changed(self):
        self.queue_draw()

class NoiseGateBox(Box):
    __gtype_name__ = 'NoiseGateBox'

    base_model = NoiseGateModels
    control_model = None
    control_enable = GATE_Enable
    has_control = True

    box_name = 'Gate'

    width = 150
    height = 90
    xdiff = 50

    def changed(self):
        self.queue_draw()

    def is_enabled(self):
        return line6control.pod.Pod.get().get_param(GATE_Thresh) != 96

class ReverbBox(Box):
    __gtype_name__ = 'ReverbBox'

    base_model = ReverbModels
    control_model = REVERB_Model
    control_enable = REVERB_Enable

    box_name = 'Reverb'

    width = 450
    height = 90
    xdiff = 50
