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

import cairo
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gi.repository import Gdk

import math
import time

from controls import *
import pod
from .resources import Resources

freq_table = [ [50.0, 55.0, 60.0, 65.0, 70.0, 75.0, 80.0, 85.0,
            90.0, 95.0, 100.0, 105.0, 110.0, 115.0, 120.0, 125.0,
            130.0, 135.0, 140.0, 145.0, 150.0, 155.0, 160.0, 165.0,
            170.0, 175.0, 180.0, 185.0, 190.0, 195.0, 200.0, 205.0,
            210.0, 215.0, 220.0, 225.0, 230.0, 235.0, 240.0, 245.0,
            250.0, 255.0, 260.0, 265.0, 270.0, 275.0, 280.0, 285.0,
            290.0, 295.0, 300.0, 305.0, 310.0, 315.0, 320.0, 325.0,
            330.0, 335.0, 340.0, 345.0, 350.0, 355.0, 360.0, 365.0,
            370.0, 375.0, 380.0, 385.0, 390.0, 395.0, 400.0, 405.0,
            410.0, 415.0, 420.0, 425.0, 430.0, 435.0, 440.0, 445.0,
            450.0, 455.0, 460.0, 465.0, 470.0, 475.0, 480.0, 485.0,
            490.0, 495.0, 500.0, 505.0, 510.0, 515.0, 520.0, 525.0,
            530.0, 535.0, 540.0, 545.0, 550.0, 555.0, 560.0, 565.0,
            570.0, 575.0, 580.0, 585.0, 590.0, 595.0, 600.0, 605.0,
            610.0, 615.0, 620.0, 625.0, 630.0, 635.0, 640.0, 645.0,
            650.0, 655.0, 660.0, 665.0, 670.0, 675.0, 680.0, 690.0],
            [50.0, 55.0, 60.0, 65.0, 70.0, 75.0, 80.0, 85.0,
            90.0, 95.0, 100.0, 105.0, 110.0, 115.0, 120.0, 125.0,
            130.0, 140.0, 150.0, 160.0, 170.0, 180.0, 190.0, 200.0,
            210.0, 220.0, 230.0, 240.0, 250.0, 260.0, 270.0, 280.0,
            290.0, 300.0, 310.0, 320.0, 330.0, 340.0, 350.0, 360.0,
            370.0, 380.0, 390.0, 400.0, 410.0, 420.0, 430.0, 440.0,
            450.0, 500.0, 550.0, 600.0, 650.0, 700.0, 750.0, 800.0,
            850.0, 900.0, 950.0, 1000.0, 1050.0, 1100.0, 1150.0, 1200.0,
            1250.0, 1300.0, 1350.0, 1400.0, 1450.0, 1500.0, 1550.0, 1600.0,
            1650.0, 1700.0, 1750.0, 1800.0, 1850.0, 1900.0, 1950.0, 2000.0,
            2050.0, 2100.0, 2150.0, 2200.0, 2250.0, 2300.0, 2350.0, 2400.0,
            2450.0, 2500.0, 2550.0, 2600.0, 2650.0, 2700.0, 2750.0, 2800.0,
            2850.0, 2900.0, 3000.0, 3100.0, 3200.0, 3300.0, 3400.0, 3500.0,
            3600.0, 3700.0, 3800.0, 3900.0, 4000.0, 4100.0, 4200.0, 4300.0,
            4400.0, 4500.0, 4600.0, 4700.0, 4800.0, 4900.0, 5000.0, 5100.0,
            5200.0, 5300.0, 5400.0, 5500.0, 5600.0, 5700.0, 5800.0, 6000.0],
            [100.0, 150.0, 200.0, 250.0, 300.0, 350.0, 400.0, 450.0,
            500.0, 550.0, 600.0, 650.0, 700.0, 750.0, 800.0, 850.0,
            900.0, 950.0, 1000.0, 1050.0, 1100.0, 1150.0, 1200.0, 1250.0,
            1300.0, 1350.0, 1400.0, 1450.0, 1500.0, 1550.0, 1600.0, 1650.0,
            1700.0, 1800.0, 1900.0, 2000.0, 2100.0, 2200.0, 2300.0, 2400.0,
            2500.0, 2600.0, 2700.0, 2800.0, 2900.0, 3000.0, 3100.0, 3200.0,
            3300.0, 3400.0, 3500.0, 3600.0, 3700.0, 3800.0, 3900.0, 4000.0,
            4100.0, 4200.0, 4300.0, 4400.0, 4500.0, 4600.0, 4700.0, 4800.0,
            4900.0, 5000.0, 5100.0, 5200.0, 5300.0, 5400.0, 5500.0, 5600.0,
            5700.0, 5800.0, 5900.0, 6000.0, 6100.0, 6200.0, 6300.0, 6400.0,
            6500.0, 6600.0, 6700.0, 6800.0, 6900.0, 7000.0, 7100.0, 7200.0,
            7300.0, 7400.0, 7500.0, 7600.0, 7700.0, 7800.0, 7900.0, 8000.0,
            8100.0, 8200.0, 8300.0, 8400.0, 8500.0, 8600.0, 8700.0, 8800.0,
            8900.0, 9000.0, 9100.0, 9200.0, 9300.0, 9400.0, 9500.0, 9600.0,
            9700.0, 9800.0, 9900.0, 10000.0, 10100.0, 10200.0, 10300.0, 10400.0,
            10500.0, 10600.0, 10700.0, 10800.0, 10900.0, 11000.0, 11100.0, 11300.0],
            [500.0, 525.0, 550.0, 575.0, 600.0, 625.0, 650.0, 675.0,
            700.0, 725.0, 750.0, 775.0, 800.0, 825.0, 850.0, 875.0,
            900.0, 925.0, 950.0, 975.0, 1000.0, 1025.0, 1050.0, 1075.0,
            1100.0, 1125.0, 1150.0, 1175.0, 1200.0, 1225.0, 1250.0, 1275.0,
            1300.0, 1350.0, 1400.0, 1450.0, 1500.0, 1550.0, 1600.0, 1650.0,
            1700.0, 1750.0, 1800.0, 1850.0, 1900.0, 1950.0, 2000.0, 2050.0,
            2100.0, 2150.0, 2200.0, 2250.0, 2300.0, 2350.0, 2400.0, 2450.0,
            2500.0, 2550.0, 2600.0, 2650.0, 2700.0, 2750.0, 2800.0, 2850.0,
            2900.0, 3000.0, 3100.0, 3200.0, 3300.0, 3400.0, 3500.0, 3600.0,
            3700.0, 3800.0, 3900.0, 4000.0, 4100.0, 4200.0, 4300.0, 4400.0,
            4500.0, 4600.0, 4700.0, 4800.0, 4900.0, 5000.0, 5100.0, 5200.0,
            5300.0, 5400.0, 5500.0, 5600.0, 5700.0, 5800.0, 5900.0, 6000.0,
            6100.0, 6200.0, 6300.0, 6400.0, 6500.0, 6600.0, 6700.0, 6800.0,
            6900.0, 7000.0, 7100.0, 7200.0, 7300.0, 7400.0, 7500.0, 7600.0,
            7700.0, 7800.0, 7900.0, 8000.0, 8100.0, 8200.0, 8300.0, 8400.0,
            8500.0, 8600.0, 8700.0, 8800.0, 8900.0, 9000.0, 9100.0, 9300.0] ]

class EQBox(Gtk.DrawingArea):
    __gtype_name__ = 'EQBox'

    box_name = "EQ"
    width = 450
    height = 140

    control_enable = EQ_Enable
    last_button_press_event = 0

    def __init__(self):
        Gtk.DrawingArea.__init__(self)

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

    def do_draw(self, ctx):

        target = ctx.get_target()
        overlay = target.create_similar(cairo.CONTENT_COLOR_ALPHA,
                                        self.width, self.height)
        overlay_cr = cairo.Context(overlay)

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
            #color = self.style.bg_gc[0]
            #self.window.draw_rectangle(color, True,
            #        ev.area.x, ev.area.y,
            #        ev.area.width, ev.area.height)


        offset = 10
        radius = 9

        overlay_cr.arc(offset + 20, offset + 5, radius,
                - math.pi, - math.pi / 2)
        overlay_cr.arc(self.width - offset - 5, offset + 5, radius,
                - math.pi / 2, 0)
        overlay_cr.arc(self.width - offset - 5, self.height - offset - 5, radius,
                0, math.pi / 2)
        overlay_cr.arc(offset + 20, self.height - offset - 5, radius,
                math.pi / 2, math.pi)
        overlay_cr.set_source_rgba(.2, .2, .2, .5)
        overlay_cr.fill()

        def to_gain(byte):
            return (12.6 + 12.8) * float(byte) / 127.0 - 12.8

        f = [freq_table[0][pod.Pod.get().get_param(EQ_Freq1)],
            freq_table[1][pod.Pod.get().get_param(EQ_Freq2)],
            freq_table[2][pod.Pod.get().get_param(EQ_Freq3)],
            freq_table[3][pod.Pod.get().get_param(EQ_Freq4)]]
        # -12.8 to 12.6
        g = [to_gain(pod.Pod.get().get_param(EQ_Gain1)),
            to_gain(pod.Pod.get().get_param(EQ_Gain2)),
            to_gain(pod.Pod.get().get_param(EQ_Gain3)),
            to_gain(pod.Pod.get().get_param(EQ_Gain4))]

        plots = []

        for i in range(0, 4):
            y = ((self.height - offset) / 2 + 5 -
                 g[i] / (12.6 + 12.8) * (self.height - offset - 5 / 2))

            x_max = math.log(11300.)
            x_min = math.log(50.)
            x_log = math.log(f[i])
            x = ((self.width - offset - 5 - (offset + 20))
                 * (x_log - x_min) / (x_max - x_min) + offset + 20)
            plots.append((x, y))

        for i, p in enumerate(plots):
            x, y = p
            if i == 0:
                overlay_cr.move_to(x, y)
            else:
                overlay_cr.line_to(x, y)
        overlay_cr.set_source_rgb(.8, .8, .8)
        overlay_cr.stroke()

        for i, p in enumerate(plots):
            x, y = p
            overlay_cr.arc(x, y, 3, 0., 2 * math.pi)
            overlay_cr.set_source_rgb(.8, .8, .8)
            overlay_cr.fill()
            overlay_cr.stroke()

        self.show_title(overlay_cr)

        ctx.set_source_surface(overlay, 0, 0)
        ctx.paint()

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
        print("changed")
        self.queue_draw()

    def is_enabled(self):
        return pod.Pod.get().get_boolean_param(self.control_enable)

    def toggle_enabled(self):
        pod.Pod.get().set_boolean_param(self.control_enable, not self.is_enabled())
        self.queue_draw()
