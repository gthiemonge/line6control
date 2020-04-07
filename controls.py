#!/usr/bin/env python
#  controls.py - MIDI/USB control values
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

# Midi control codes
AMP_Model              = 12     # 0..32  (11 or 12 ?)
AMP_Drive              = 13     # 0..127
AMP_Bass               = 14     # 0..127
AMP_Mid                = 15     # 0..127
AMP_Treble             = 16     # 0..127
AMP_Presence           = 21     # 0..127
AMP_ChanVol            = 17     # 0..127
AMP_Pan                = 10     # 0..127 (no transmit)  0=left, 64=center, 127=right

CAB_Model              = 71     # 0..25
MIC_Select             = 70     # 0..3
ROOM_Level             = 76     # 0..127

COMP_Gain              = 5
COMP_Thresh            = 9
COMP_Enable            = 26

GATE_Thresh            = 23
GATE_Decay             = 24
GATE_Enable            = 22

STOMP_Model            = 75     # 0..9
STOMP_Param1           = 27     # 0..127 (not used)
STOMP_Param1_NoteValue = 78     # 0..127
STOMP_Param2           = 79     # 0..127
STOMP_Param3           = 80     # 0..127
STOMP_Param4           = 81     # 0..127
STOMP_Param5           = 82     # 0..127
STOMP_VolumeMix        = 83     # 0..127
STOMP_Enable           = 25     # 0..63=off, 64..127=on

MOD_Model              = 58
MOD_Param1             = 29
MOD_Param1_DoublePrec  = 61
MOD_Param1_NoteValue   = 51
MOD_Param2             = 52
MOD_Param3             = 53
MOD_Param4             = 54
MOD_Param5             = 55
MOD_VolumeMix          = 56
MOD_PrePost            = 57
MOD_Enable             = 50

DELAY_Model            = 88
DELAY_Param1           = 30
DELAY_Param1_DoublePrec= 62
DELAY_Param1_NoteValue = 31
DELAY_Param2           = 33
DELAY_Param3           = 35
DELAY_Param4           = 85
DELAY_Param5           = 86
DELAY_VolumeMix        = 34
DELAY_PrePost          = 87
DELAY_Enable           = 28

AMP_Enable             = 111    # 0..63=off, 64..127=on

REVERB_Level           = 18
REVERB_Enable          = 36
REVERB_Model           = 37
REVERB_Decay           = 38
REVERB_Tone            = 39
REVERB_PreDelay        = 40
REVERB_PrePost         = 41

TWEAK                  = 1

WAH_Position           = 4
WAH_Enable             = 43

VOLUME_Pedal           = 7
VOLUME_Minimum         = 46
VOLUME_PrePost         = 47

EQ_Enable              = 63
EQ_Freq1               = 20
EQ_Freq2               = 42
EQ_Freq3               = 60
EQ_Freq4               = 77
EQ_Gain1               = 114
EQ_Gain2               = 116
EQ_Gain3               = 117
EQ_Gain4               = 119


class Control:
    type = "Control"

    def __init__(self, control_id, name):
        self.control_id = control_id
        self.name = name

class Knob(Control):
    type = "Knob"

    def __init__(self, control_id, name, phys_range, device_range, unit = ''):
        Control.__init__(self, control_id, name)

        self.phys_range = phys_range
        self.device_range = device_range
        self.unit = unit


class Controls:
    def __init__(self, name, realname, controls = None):
        self.name = name
        self.realname = realname
        self.controls = controls

class EffectControls(Controls):
    type = "Effect"

    def __init__(self, name, realname, controls):
        Controls.__init__(self, name, realname, controls)

class AmpControls(Controls):
    type = "Amp"

    def __init__(self, name, realname = None):
        if realname == None:
            realname = name
        Controls.__init__(self, name, realname,
                          (Knob(AMP_Drive, 'DRIVE', (0, 100), (0, 127), '%'),
                           Knob(AMP_Bass, 'BASS', (0, 100), (0, 127), '%'),
                           Knob(AMP_Mid, 'MID', (0, 100), (0, 127), '%'),
                           Knob(AMP_Treble, 'TREBLE', (0, 100), (0, 127), '%'),
                           Knob(AMP_Presence, 'PRESENCE', (0, 100), (0, 127), '%'),
                           Knob(AMP_ChanVol, 'CHAN VOL', (0, 100), (0, 127), '%')))

class CabControls(Controls):
    type = "Cab"

    def __init__(self, name, realname = None):
        if realname == None:
            realname = name
        Controls.__init__(self, name, realname)


AmpModels = {
    0 : AmpControls('Bypass'),
    1 : AmpControls('Tube Preamp'),
    2 : AmpControls('Line 6 Clean'),
    3 : AmpControls('Line 6 JTS-45'),
    4 : AmpControls('Line 6 Class A'),
    5 : AmpControls('Line 6 Mood'),
    6 : AmpControls('Spinal Puppet'),
    7 : AmpControls('Line 6 Chem X'),
    8 : AmpControls('Line 6 Insane'),
    9 : AmpControls('Line 6 Aco 2'),
    10 : AmpControls('Zen Master', 'Budda Twinmaster 2x12 Combo'),
    11 : AmpControls('Small Tweed', '\'53 Fender Deluxe'),
    12 : AmpControls('Tweed B-Man', '\'58 Fender Bassman'),
    13 : AmpControls('Tiny Tweed', '\'61 Tweed Fender Champ'),
    14 : AmpControls('Blackface Lux', '\'64 Fender Deluxe Reverb'),
    15 : AmpControls('Double Verb', '\'65 Fender Blackface Twin'),
    16 : AmpControls('Two-Tone', 'Gretsch 6156'),
    17 : AmpControls('Hiway 100', 'Hiwatt Custom 100'),
    18 : AmpControls('Plexi 45', '\'65 Marshall JTM-45'),
    19 : AmpControls('Plexi Lead', '\'68 Marshall \'Plexi\' Super Lead'),
    20 : AmpControls('Plexi Jump Lead', 'Jumpered Marshall Super Lead'),
    21 : AmpControls('Plexi Variac', 'Variac\'d Marshall Super Lead'),
    22 : AmpControls('Brit J-800', 'Marshall JCM 800'),
    23 : AmpControls('Brit JM Pre', 'Marshall JMP-1 Preamp'),
    24 : AmpControls('Match Chief', '\'96 Matchless Chieftain'),
    25 : AmpControls('Match D-30', 'Matchless DC-30'),
    26 : AmpControls('Treadplate', '2001 Mesa Boogie Dual Rectifier'),
    27 : AmpControls('Cali Crunch', '\'85 Mesa Boogie Mark IIC+'),
    28 : AmpControls('Jazz Clean', '\'87 Roland JC-120'),
    29 : AmpControls('Solo 100', 'Soldano SLO-100 Head'),
    30 : AmpControls('Super O', 'Supro S6616'),
    31 : AmpControls('Class A-15', '\'60 Vox AC-15'),
    32 : AmpControls('Class A-30 TB', '\'67 Vox AC-30 Top Boost'),
    33 : AmpControls('Line 6 Agro'),
    34 : AmpControls('Line 6 Lunatic'),
    35 : AmpControls('Line 6 Treadplate'),
    36 : AmpControls('Variax Acoustic'),
    101 : AmpControls('Citrus D-30', '2005 Orange AD30TC'),
    102 : AmpControls('Line 6 Modern High Gain #1'),
    103 : AmpControls('Line 6 Boutique #1'),
    104 : AmpControls('Class A-30 Fawn', 'Non Top Boost Vox AC-30'),
    105 : AmpControls('Brit Gain 18', 'Marshall 1974X "authentic re-issue"'),
    106 : AmpControls('Brit J-2000 #2', 'Marshall JCM2000 DSL')
    }

CabModels = {
    0 : CabControls('No Cab'),
    1 : CabControls('1x6 Super O'),
    2 : CabControls('1x8 Tweed'),
    3 : CabControls('1x10 Gibtone'),
    4 : CabControls('1x10 G-Brand'),
    5 : CabControls('1x12 Line 6'),
    6 : CabControls('1x12 Tweed'),
    7 : CabControls('1x12 Blackface'),
    8 : CabControls('1x12 Class A'),
    9 : CabControls('2x2 Mini T'),
    10 : CabControls('2x12 Line 6'),
    11 : CabControls('2x12 Blackface'),
    12 : CabControls('2x12 Match'),
    13 : CabControls('2x12 Jazz'),
    14 : CabControls('2x12 Class A'),
    15 : CabControls('4x10 Line 6'),
    16 : CabControls('4x10 Tweed'),
    17 : CabControls('4x12 Line 6'),
    18 : CabControls('4x12 Green 20\'s'),
    19 : CabControls('4x12 Green 25\'s'),
    20 : CabControls('4x12 Brit T75'),
    21 : CabControls('4x12 Brit V30\'s'),
    22 : CabControls('4x12 Treadplate'),
    23 : CabControls('1x15 Thunder'),
    24 : CabControls('2x12 Wishbook')
    }

CompModels = {
    0 : EffectControls('Compressor', '',
                       (Knob(COMP_Thresh, 'THRESH', (-63, 0), (0, 126), 'dB'),
                        Knob(COMP_Gain, 'GAIN', (0, 16), (0, 127), 'dB')))
    }

NoiseGateModels = {
    0 : EffectControls('Noise Gate', '',
                       (Knob(GATE_Thresh, 'THRESH', (0, -96), (0, 96), 'dB'),
                        Knob(GATE_Decay, 'DECAY', (0, 100), (0, 127), '%')))
    }

StompModels = {
    # (Line 6 Name, Real Name, Controls)
    0 : EffectControls('Facial Fuzz', 'Fuzz Face',
                      (Knob(STOMP_Param2, 'DRIVE', (0, 100), (0, 127), '%'),
                       Knob(STOMP_Param3, 'GAIN', (0, 100), (0, 127), '%'),
                       Knob(STOMP_Param4, 'TONE', (0, 100), (0, 127), '%'))),
    1 : EffectControls('Fuzz Pi', 'Big Muff Pi',
                      (Knob(STOMP_Param2, 'DRIVE', (0, 100), (0, 127), '%'),
                       Knob(STOMP_Param3, 'GAIN', (0, 100), (0, 127), '%'),
                       Knob(STOMP_Param4, 'TONE', (0, 100), (0, 127), '%'))),
    2 : EffectControls('Screamer', 'TS-808',
                      (Knob(STOMP_Param2, 'DRIVE', (0, 100), (0, 127), '%'),
                       Knob(STOMP_Param3, 'GAIN', (0, 100), (0, 127), '%'),
                       Knob(STOMP_Param4, 'TONE', (0, 100), (0, 127), '%'))),
    3 : EffectControls('Classic Dist', 'ProCo Rat',
                      (Knob(STOMP_Param2, 'DRIVE', (0, 100), (0, 127), '%'),
                       Knob(STOMP_Param3, 'GAIN', (0, 100), (0, 127), '%'),
                       Knob(STOMP_Param4, 'TONE', (0, 100), (0, 127), '%'))),
    4 : EffectControls('Octave Fuzz', 'Octavia',
                      (Knob(STOMP_Param2, 'DRIVE', (0, 100), (0, 127), '%'),
                       Knob(STOMP_Param3, 'GAIN', (0, 100), (0, 127), '%'),
                       Knob(STOMP_Param4, 'TONE', (0, 100), (0, 127), '%'))),
    5 : EffectControls('Blue Comp', 'Boss CS-1',
                      (Knob(STOMP_Param2, 'SUSTAIN', (0, 100), (0, 127), '%'),
                       Knob(STOMP_Param3, 'LEVEL', (0, 100), (0, 127), '%'))),
    6 : EffectControls('Red Comp', 'MXR Dyna Comp',
                      (Knob(STOMP_Param2, 'SUSTAIN', (0, 100), (0, 127), '%'),
                       Knob(STOMP_Param3, 'LEVEL', (0, 100), (0, 127), '%'))),
    7 : EffectControls('Vetta Comp', 'Line 6 Vetta Comp',
                      (Knob(STOMP_Param2, 'SENS', (0, 100), (0, 127), '%'),
                       Knob(STOMP_Param3, 'LEVEL', (0, 100), (0, 127), '%'))),
    8 : EffectControls('Auto Swell', 'Line 6 Auto Swell',
                      (Knob(STOMP_Param2, 'RAMP', (0, 100), (0, 127), '%'),
                       Knob(STOMP_Param3, 'DEPTH', (0, 100), (0, 127), '%'))),
    9 : EffectControls('Auto Wah', 'Mutron III',
                      (Knob(STOMP_Param2, 'SENS', (0, 100), (0, 127), '%'),
                       Knob(STOMP_Param3, 'Q', (0, 100), (0, 127), '%'))),
    27 : EffectControls('Bass Overdrive', '',
                       (Knob(STOMP_Param4, 'DRIVE', (0, 100), (0, 127), '%'),
                        Knob(STOMP_Param5, 'GAIN', (0, 100), (0, 127), '%'),
                        Knob(STOMP_Param2, 'BASS', (0, 100), (0, 127), '%'),
                        Knob(STOMP_Param3, 'TREBLE', (0, 100), (0, 127), '%'))),
    28 : EffectControls('Bronze Master', '',
                        (Knob(STOMP_Param2, 'DRIVE', (0, 100), (0, 127), '%'),
                         Knob(STOMP_Param3, 'TONE', (0, 100), (0, 127), '%'),
                         Knob(STOMP_Param5, 'BLEND', (0, 100), (0, 127), '%'))),
    29 : EffectControls('Sub Octaves', '',
                       (Knob(STOMP_Param2, '-10CTG', (0, 100), (0, 127), '%'),
                        Knob(STOMP_Param3, '-20CTG', (0, 100), (0, 127), '%'),
                        Knob(STOMP_Param5, 'MIX', (0, 100), (0, 127), '%'))),
    30 : EffectControls('Bender', '',
                       (Knob(STOMP_Param5, 'MIX', (0, 100), (0, 127), '%'),
                        Knob(STOMP_Param3, 'HEEL', (-24, 24), (16, 112)),
                        Knob(STOMP_Param4, 'TOE', (-24, 24), (16, 112)),
                        Knob(STOMP_Param2, 'POSI', (0, 100), (0, 127), '%')))
    }

ModModels = {
    0 : EffectControls('Sine Chorus', '',
                       (Knob(MOD_Param1, 'SPEED', (0, 100), (0, 127), '%'),
                        Knob(MOD_Param2, 'DEPTH', (0, 100), (0, 127), '%'),
                        Knob(MOD_VolumeMix, 'MIX', (0, 100), (0, 127), '%'),
                        Knob(MOD_Param3, 'BASS', (0, 100), (0, 127), '%'),
                        Knob(MOD_Param4, 'TREBLE', (0, 100), (0, 127), '%'),
                        Knob(MOD_PrePost, 'PRE/POST', (0, 100), (0, 127), '%'))),
    1 : EffectControls('Analog Chorus', '',
                       (Knob(MOD_Param1, 'SPEED', (0, 100), (0, 127), '%'),
                        Knob(MOD_Param2, 'DEPTH', (0, 100), (0, 127), '%'),
                        Knob(MOD_VolumeMix, 'MIX', (0, 100), (0, 127), '%'),
                        Knob(MOD_Param3, 'BASS', (0, 100), (0, 127), '%'),
                        Knob(MOD_Param4, 'TREBLE', (0, 100), (0, 127), '%'),
                        Knob(MOD_PrePost, 'PRE/POST', (0, 100), (0, 127), '%'))),
    2 : EffectControls('Line 6 Flanger', '',
                       (Knob(MOD_Param1, 'SPEED', (0, 100), (0, 127), '%'),
                        Knob(MOD_Param2, 'DEPTH', (0, 100), (0, 127), '%'),
                        Knob(MOD_VolumeMix, 'MIX', (0, 100), (0, 127), '%'),
                        Knob(MOD_PrePost, 'PRE/POST', (0, 100), (0, 127), '%'))),
    3 : EffectControls('Jet Flanger', '',
                       (Knob(MOD_Param1, 'SPEED', (0, 100), (0, 127), '%'),
                        Knob(MOD_Param2, 'DEPTH', (0, 100), (0, 127), '%'),
                        Knob(MOD_VolumeMix, 'MIX', (0, 100), (0, 127), '%'),
                        Knob(MOD_Param3, 'FDBK', (0, 100), (0, 127), '%'),
                        Knob(MOD_Param4, 'MANUAL', (0, 100), (0, 127), '%'),
                        Knob(MOD_PrePost, 'PRE/POST', (0, 100), (0, 127), '%'))),
    4 : EffectControls('Phaser', '',
                       (Knob(MOD_Param1, 'SPEED', (0, 100), (0, 127), '%'),
                        Knob(MOD_Param2, 'FDKB', (0, 100), (0, 127), '%'),
                        Knob(MOD_VolumeMix, 'MIX', (0, 100), (0, 127), '%'),
                        Knob(MOD_PrePost, 'PRE/POST', (0, 100), (0, 127), '%'))),
    5 : EffectControls('U-Vibe', '',
                       (Knob(MOD_Param1, 'SPEED', (0, 100), (0, 127), '%'),
                        Knob(MOD_Param2, 'DEPTH', (0, 100), (0, 127), '%'),
                        Knob(MOD_VolumeMix, 'MIX', (0, 100), (0, 127), '%'),
                        Knob(MOD_PrePost, 'PRE/POST', (0, 100), (0, 127), '%'))),
    6 : EffectControls('Opto Trem', '',
                       (Knob(MOD_Param1, 'SPEED', (0, 100), (0, 127), '%'),
                        Knob(MOD_Param2, 'WAVE', (0, 100), (0, 127), '%'),
                        Knob(MOD_VolumeMix, 'MIX', (0, 100), (0, 127), '%'),
                        Knob(MOD_PrePost, 'PRE/POST', (0, 100), (0, 127), '%'))),
    7 : EffectControls('Bias Trem', '',
                       (Knob(MOD_Param1, 'SPEED', (0, 100), (0, 127), '%'),
                        Knob(MOD_Param2, 'WAVE', (0, 100), (0, 127), '%'),
                        Knob(MOD_VolumeMix, 'MIX', (0, 100), (0, 127), '%'),
                        Knob(MOD_PrePost, 'PRE/POST', (0, 100), (0, 127), '%'))),
    8 : EffectControls('Rotary Drum + Horn', '',
                       (Knob(MOD_Param1, 'SPEED', (0, 100), (0, 127), '%'),
                        Knob(MOD_Param2, 'TONE', (0, 100), (0, 127), '%'),
                        Knob(MOD_VolumeMix, 'MIX', (0, 100), (0, 127), '%'),
                        Knob(MOD_PrePost, 'PRE/POST', (0, 100), (0, 127), '%'))),
    9 : EffectControls('Rotary Drum', '',
                       (Knob(MOD_Param1, 'SPEED', (0, 100), (0, 127), '%'),
                        Knob(MOD_Param2, 'TONE', (0, 100), (0, 127), '%'),
                        Knob(MOD_VolumeMix, 'MIX', (0, 100), (0, 127), '%'),
                        Knob(MOD_PrePost, 'PRE/POST', (0, 100), (0, 127)))),
    10 : EffectControls('Auto Pan', '',
                       (Knob(MOD_Param1, 'SPEED', (0, 100), (0, 127), '%'),
                        Knob(MOD_Param2, 'WAVE', (0, 100), (0, 127), '%'),
                        Knob(MOD_VolumeMix, 'MIX', (0, 100), (0, 127), '%'),
                        Knob(MOD_PrePost, 'PRE/POST', (0, 100), (0, 127), '%')))
    }

DelayModels = {
    0 : EffectControls('Analog Delay', '',
                       (Knob(DELAY_Param1_NoteValue, 'TIME', (0, 100), (0, 127), '%'),
                        Knob(DELAY_Param2, 'FDBK', (0, 100), (0, 127), '%'),
                        Knob(DELAY_VolumeMix, 'MIX', (0, 100), (0, 127), '%'),
                        Knob(DELAY_Param3, 'BASS', (0, 100), (0, 127), '%'),
                        Knob(DELAY_Param4, 'TREBLE', (0, 100), (0, 127), '%'),
                        Knob(DELAY_PrePost, 'PRE/POST', (0, 100), (0, 127), '%'))),
    1 : EffectControls('Analog w/Mod', '',
                       (Knob(DELAY_Param1_NoteValue, 'TIME', (0, 100), (0, 127), '%'),
                        Knob(DELAY_Param2, 'FDBK', (0, 100), (0, 127), '%'),
                        Knob(DELAY_VolumeMix, 'MIX', (0, 100), (0, 127), '%'),
                        Knob(DELAY_Param3, 'MODSPD', (0, 100), (0, 127), '%'),
                        Knob(DELAY_Param4, 'DEPTH', (0, 100), (0, 127), '%'),
                        Knob(DELAY_PrePost, 'PRE/POST', (0, 100), (0, 127), '%'))),
    2 : EffectControls('Tube Echo', '',
                       (Knob(DELAY_Param1_NoteValue, 'TIME', (0, 100), (0, 127), '%'),
                        Knob(DELAY_Param2, 'FDBK', (0, 100), (0, 127), '%'),
                        Knob(DELAY_VolumeMix, 'MIX', (0, 100), (0, 127), '%'),
                        Knob(DELAY_Param3, 'FLUT', (0, 100), (0, 127), '%'),
                        Knob(DELAY_Param4, 'DRIVE', (0, 100), (0, 127), '%'),
                        Knob(DELAY_PrePost, 'PRE/POST', (0, 100), (0, 127), '%'))),
    3 : EffectControls('Multi-Head', '',
                       (Knob(DELAY_Param1_NoteValue, 'TIME', (0, 100), (0, 127), '%'),
                        Knob(DELAY_Param2, 'FDBK', (0, 100), (0, 127), '%'),
                        Knob(DELAY_VolumeMix, 'MIX', (0, 100), (0, 127), '%'),
                        Knob(DELAY_Param3, 'HEADS', (0, 100), (0, 127), '%'),
                        Knob(DELAY_Param4, 'FLUT', (0, 100), (0, 127), '%'),
                        Knob(DELAY_PrePost, 'PRE/POST', (0, 100), (0, 127), '%'))),
    4 : EffectControls('Sweep Echo', '',
                       (Knob(DELAY_Param1_NoteValue, 'TIME', (0, 100), (0, 127), '%'),
                        Knob(DELAY_Param2, 'FDBK', (0, 100), (0, 127), '%'),
                        Knob(DELAY_VolumeMix, 'MIX', (0, 100), (0, 127), '%'),
                        Knob(DELAY_Param3, 'SPEED', (0, 100), (0, 127), '%'),
                        Knob(DELAY_Param4, 'DEPTH', (0, 100), (0, 127), '%'),
                        Knob(DELAY_PrePost, 'PRE/POST', (0, 100), (0, 127), '%'))),
    5 : EffectControls('Digital Delay', '',
                       (Knob(DELAY_Param1_NoteValue, 'TIME', (0, 100), (0, 127), '%'),
                        Knob(DELAY_Param2, 'FDBK', (0, 100), (0, 127), '%'),
                        Knob(DELAY_VolumeMix, 'MIX', (0, 100), (0, 127), '%'),
                        Knob(DELAY_Param3, 'BASS', (0, 100), (0, 127), '%'),
                        Knob(DELAY_Param4, 'TREBLE', (0, 100), (0, 127), '%'),
                        Knob(DELAY_PrePost, 'PRE/POST', (0, 100), (0, 127), '%'))),
    6 : EffectControls('Stereo Delay', '',
                       (Knob(DELAY_Param1_NoteValue, 'TIME', (0, 100), (0, 127), '%'),
                        Knob(DELAY_Param2, 'OFFSET', (0, 100), (0, 127), '%'),
                        Knob(DELAY_VolumeMix, 'MIX', (0, 100), (0, 127), '%'),
                        Knob(DELAY_Param3, 'FDBK L', (0, 100), (0, 127), '%'),
                        Knob(DELAY_Param4, 'FDBK R', (0, 100), (0, 127), '%'),
                        Knob(DELAY_PrePost, 'PRE/POST', (0, 100), (0, 127), '%'))),
    7 : EffectControls('Ping Pong', '',
                       (Knob(DELAY_Param1_NoteValue, 'TIME', (0, 100), (0, 127), '%'),
                        Knob(DELAY_Param2, 'FDBK', (0, 100), (0, 127), '%'),
                        Knob(DELAY_VolumeMix, 'MIX', (0, 100), (0, 127), '%'),
                        Knob(DELAY_Param3, 'OFFSET', (0, 100), (0, 127), '%'),
                        Knob(DELAY_Param4, 'SPRED', (0, 100), (0, 127), '%'),
                        Knob(DELAY_PrePost, 'PRE/POST', (0, 100), (0, 127), '%'))),
    8 : EffectControls('Reverse', '',
                       (Knob(DELAY_Param1_NoteValue, 'TIME', (0, 100), (0, 127), '%'),
                        Knob(DELAY_Param2, 'FDBK', (0, 100), (0, 127), '%'),
                        Knob(DELAY_VolumeMix, 'MIX', (0, 100), (0, 127), '%'),
                        Knob(DELAY_PrePost, 'PRE/POST', (0, 100), (0, 127), '%')))
    }
