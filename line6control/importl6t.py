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

from .controls import *
import line6control.pod
import sys
from struct import unpack

Preset_Name = slice(7, 23)

M_GATE       = 0x20000
M_VOL_PRE    = 0x20001
M_WAH        = 0x20002
M_STOMP_PRE  = 0x20003
M_MOD_PRE    = 0x20004
M_DELAY_PRE  = 0x20005
M_REV_PRE    = 0x20006

M_AMP        = 0x30000
M_CAB        = 0x30001
M_TREM       = 0x30002
M_AIR        = 0x30003

M_COMP       = 0x50000
M_STOMP_POST = 0x50001
M_VOL_POST   = 0x50002
M_MOD_POST   = 0x50003
M_DELAY_POST = 0x50004
M_REV_POST   = 0x50005

# L6T/GPT Amps Id to Device Amp Id
L6TAmps = {
    0: 0,
    1: 2,
    2: 0,
    3: 0,
    4: 0,
    5: 3,
    6: 0,
    7: 5,
    8: 6,
    9: 0,
    10: 7,
    11: 0,
    12: 8,
    13: 0,
    14: 0,
    15: 9,
    16: 10,
    17: 11,
    18: 12,
    19: 13,
    20: 14,
    21: 15,
    22: 0,
    23: 0,
    24: 16,
    25: 17,
    26: 18,
    27: 19,
    28: 0,
    29: 20,
    30: 21,
    31: 0,
    32: 22,
    33: 23,
    34: 24,
    35: 25,
    36: 26,
    37: 0,
    38: 27,
    39: 28,
    40: 0,
    41: 29,
    42: 30,
    43: 0,
    44: 31,
    45: 32,
    46: 2,
    47: 0,
    48: 0,
    49: 33,
    50: 0,
    51: 0,
    52: 35,
    53: 0,
    # TODO
    59: 35 # XXX ??
}

L6TCabs = {
    0: 0,
    1: 1,
    2: 2,
    3: 3,
    4: 4,
    5: 5,
    6: 6,
    7: 7,
    8: 8,
    9: 9,
    10: 10,
    11: 11,
    12: 12,
    13: 13,
    14: 14,
    15: 15,
    16: 16,
    17: 17,
    18: 18,
    19: 19,
    20: 20,
    21: 21,
    22: 22,
    #TODO
}

L6TStomps = {

}

class ImportL6T:
    def __init__(self, filename):
        self.filename = filename
        self.buffer = [0 for i in range(0, 168+4)]

    def parse(self):
        self.current_minf = None
        self.f = open(self.filename, 'rb')

        while True:
            h = self.read_header()
            if h == "FORM":
                self.read_int()

            elif h == "L6PA":
                pass

            elif h == "PINF":
                buf = self.read(76)
                name = "".join(map(chr, buf[13:])).replace('\x00', '')
                self.buffer[Preset_Name] = name
                self.buffer[Preset_Name.start + len(name):Preset_Name.stop] = [ 0x20 for x in range(0, Preset_Name.stop - Preset_Name.start - len(name)) ]
                self.read(4)
            elif h == "LIST":
                self.read_int()

            elif h == "PATC":
                pass

            elif h == "MODL":
                pass

            elif h == "MINF":
                self.read_int() # size
                d = self.read_int()
                d = d & 0xffff

                self.current_minf = self.read_int() # slotID

                self.read_byte() # ordinal
                self.read_byte()
                self.read_byte()

                if self.read_byte() != 0:
                    enabled = 0x7f
                else:
                    enabled = 0

                print("%05x-%2x-%x" % (self.current_minf, d, enabled))

                if self.current_minf == M_AMP: # TODO : check this
                    self.buffer[0x27 + AMP_Model] = L6TAmps[d]
                    self.buffer[0x27 + AMP_Enable] = enabled

                elif self.current_minf == M_CAB:
                    self.buffer[0x27 + CAB_Model] = L6TCabs[d]

                elif self.current_minf == M_AIR:
                    self.buffer[0x27 + MIC_Select] = d - 1

                elif self.current_minf == M_GATE:
                    self.buffer[0x27 + GATE_Enable] = enabled

                elif self.current_minf == M_VOL_PRE or self.current_minf == M_VOL_POST:
                    self.buffer[0x27 + VOLUME_Pedal] = enabled

                elif self.current_minf == M_WAH:
                    self.buffer[0x27 + WAH_Enable] = enabled

                elif self.current_minf == M_REV_PRE or self.current_minf == M_REV_POST:
                    self.buffer[0x27 + REVERB_Model] = d
                    self.buffer[0x27 + REVERB_Enable] = enabled

                elif self.current_minf == M_COMP:
                    self.buffer[0x27 + COMP_Enable] = enabled

                elif self.current_minf == M_STOMP_PRE or self.current_minf == M_STOMP_POST:
                    self.buffer[0x27 + STOMP_Model] = d
                    self.buffer[0x27 + STOMP_Enable] = enabled

                elif self.current_minf == M_MOD_PRE or self.current_minf == M_MOD_POST:
                    self.buffer[0x27 + MOD_Model] = d
                    self.buffer[0x27 + MOD_Enable] = enabled

                elif self.current_minf == M_DELAY_PRE or self.current_minf == M_DELAY_POST:
                    self.buffer[0x27 + DELAY_Model] = d
                    self.buffer[0x27 + DELAY_Enable] = enabled

            elif h == "PARM":
                self.read_int() # size

                self.read_byte()
                type_2 = self.read_byte()
                self.read_byte()
                type = self.read_byte()

                self.read_int() # valueType

                print("%05x %2d %2d" % (self.current_minf, type, type_2))
                if self.current_minf == M_AMP:
                    value = int(self.read_float() * 128)
                    if type == 0:
                        self.buffer[0x27 + AMP_Bass] = value
                    elif type == 1:
                        self.buffer[0x27 + AMP_Mid] = value
                    elif type == 2:
                        self.buffer[0x27 + AMP_Treble] = value
                    elif type == 3:
                        self.buffer[0x27 + AMP_Drive] = value
                    elif type == 4:
                        self.buffer[0x27 + AMP_Presence] = value
                    elif type == 5:
                        self.buffer[0x27 + AMP_ChanVol] = value
                    elif type == 6:
                        self.buffer[0x27 + AMP_Pan] = value

                elif self.current_minf == M_CAB:
                    value = int(self.read_float() * 128)
                    #print("%d %d %x" % (type, type_2, value))

                elif self.current_minf == M_AIR:
                    value = int(self.read_float() * 128)
                    print("%d %d %x" % (type, type_2, value))
                    if type == 0:
                        self.buffer[0x27 + ROOM_Level] = value

                elif self.current_minf == M_VOL_PRE or self.current_minf == M_VOL_POST:
                    if type == 3:
                        if self.read_float() >= 0.5:
                            value = 127
                        else:
                            value = 0
                        self.buffer[0x27 + VOLUME_PrePost] = value
                    elif type == 4:
                        value = int(self.read_float() * 128)
                        self.buffer[0x27 + VOLUME_Minimum] = value

                elif self.current_minf == M_REV_PRE or self.current_minf == M_REV_POST:
                    value = int(self.read_float() * 128)
                    print("%d %d %x" % (type, type_2, value))
                    if type_2 == 1:
                        if type == 2:
                            self.buffer[0x27 + REVERB_Level] = value
                    elif type_2 == 16:
                        if type == 0:
                            self.buffer[0x27 + REVERB_Decay] = value
                        elif type == 1:
                            pass
                        elif type == 2:
                            self.buffer[0x27 + REVERB_Tone] = value

                elif self.current_minf == M_COMP:
                    if type == 0:
                        value = int(128 - self.read_float())
                        self.buffer[0x27 + COMP_Thresh] = value
                    else:
                        value = int(self.read_float() * 128)
                        self.buffer[0x27 + COMP_Gain] = value

                elif self.current_minf == M_GATE:
                    if type == 0:
                        value = - int(self.read_float())
                        self.buffer[0x27 + GATE_Thresh] = value
                    else:
                        value = int(self.read_float() * 128)
                        self.buffer[0x27 + GATE_Decay] = value

                elif self.current_minf == M_STOMP_PRE or self.current_minf == M_STOMP_POST:
                    value = int(self.read_float() * 128)
                    if type == 0:
                        self.buffer[0x27 + STOMP_Param1] = value
                    elif type == 1:
                        self.buffer[0x27 + STOMP_Param2] = value
                    elif type == 2:
                        self.buffer[0x27 + STOMP_Param3] = value
                    elif type == 3:
                        self.buffer[0x27 + STOMP_Param4] = value
                    elif type == 4:
                        self.buffer[0x27 + STOMP_Param5] = value
                    elif type == 5:
                        self.buffer[0x27 + STOMP_VolumeMix] = value
                    else:
                        print("STOMP not handled : %d %x" % (type, value))

                elif self.current_minf == M_MOD_PRE or self.current_minf == M_MOD_POST:
                    value = int(self.read_float() * 128)
                    if type_2 == 16:
                        if type == 0:
                            self.buffer[0x27 + MOD_Param1] = value
                        elif type == 1:
                            self.buffer[0x27 + MOD_Param2] = value
                        elif type == 2:
                            self.buffer[0x27 + MOD_Param3] = value
                        elif type == 3:
                            self.buffer[0x27 + MOD_Param4] = value
                        elif type == 4:
                            self.buffer[0x27 + MOD_Param5] = value
                    elif type_2 == 32:
                        pass
                    elif type_2 == 1:
                        if type == 1:
                            self.buffer[0x27 + MOD_VolumeMix] = value
                        else:
                            pass

                elif self.current_minf == M_DELAY_PRE or self.current_minf == M_DELAY_POST:
                    value = int(self.read_float() * 128)
                    if type_2 == 16:
                        if type == 0:
                            self.buffer[0x27 + DELAY_Param1] = value
                        elif type == 1:
                            self.buffer[0x27 + DELAY_Param2] = value
                        elif type == 2:
                            self.buffer[0x27 + DELAY_Param3] = value
                        elif type == 3:
                            self.buffer[0x27 + DELAY_Param4] = value
                        elif type == 4:
                            self.buffer[0x27 + DELAY_Param5] = value
                        else:
                            print("DELAY not handled : %d %x" % (type, value))
                    elif type_2 == 32:
                        print("DELAY not handled : %d %x" % (type, value))
                    elif type_2 == 1:
                        if type == 1:
                            self.buffer[0x27 + DELAY_VolumeMix] = value
                        elif type == 2:
                            print("DELAY not handled : %d %x" % (type, value))

                elif self.current_minf == M_WAH:
                    value = int(self.read_float() * 128)
                    self.buffer[0x27 + WAH_Position] = value
                else:
                    value = self.read_float()

            else:
                break

        self.f.close()

    def read(self, size):
        b = self.f.read(size)
        return b

    def read_byte(self):
        return self.read(1)[0]

    def read_int(self):
        buf = self.f.read(4)
        ret = unpack('>i', buf)[0]
        return ret

    def read_float(self):
        buf = self.f.read(4)
        ret = unpack('>f', buf)[0]
        return ret

    def read_header(self):
        buf = self.read(4)
        return buf.decode('utf-8')

if __name__ == '__main__':
    #imp = ImportL6T('marshall-jcm800.l6t')
    #imp = ImportL6T('soldano-slo100.l6t')
    imp = ImportL6T(sys.argv[1])
    imp.parse()

    i = 0
    hexstr = '%08x  ' % (i)
    charstr = ''
    for x in imp.buffer[7:]:
        if i != 0 and (i % 16) == 0:
            print("%s %s" % (hexstr, charstr))
            charstr = ''
            hexstr = '%08x  ' % (i)

        try:
            hexstr += "%02X " % (ord(x))
            if ord(x) >= 20 and ord(x) < 127:
                charstr += "%c" % (x)
            else:
                charstr += "."
        except:
            hexstr += "%02X " % (x)
            if x >= 20 and x < 127:
                charstr += "%c" % (chr(int(x)))
            else:
                charstr += "."

        i += 1
    print("%s %s" % (hexstr, charstr))
