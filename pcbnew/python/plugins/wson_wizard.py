#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#

from __future__ import division
import pcbnew

import HelpfulFootprintWizardPlugin as HFPW
import PadArray as PA


class WSONGridArray(PA.PadArray):

    def __init__(self, first_pad, yoff, pad, nx, ny, px, py, centre=pcbnew.wxPoint(0, 0)):
        PA.PadArray.__init__(self)
        # this pad is more of a "context", we will use it as a source of
        # pad data, but not actually add it
        self.SetFirstPadType(first_pad)
        self.yoff = yoff
        self.pad = pad
        self.nx = int(nx)
        self.ny = int(ny)
        self.px = px
        self.py = py
        self.centre = centre

    # right to left, top to bottom
    def NamingFunction(self, x, y):
        if y==0:
            return x+1
        else:
            return self.nx*2-x

    #relocate the pad and add it as many times as we need
    def AddPadsToModule(self, dc):

        pin1posX = self.centre.x - self.px * (self.nx - 1) / 2
        pin1posY = self.centre.y + self.py * (self.ny - 1) / 2

        for x in range(0, self.nx):
            posX = pin1posX + (x * self.px)

            for y in range(self.ny):
                if x == 0 and y == 0:
                    posY = pin1posY - (self.py * y) - self.yoff/2
                    pos = dc.TransformPoint(posX, posY)
                    pad = self.GetPad(True, pos)
                else:
                    posY = pin1posY - (self.py * y)
                    pos = dc.TransformPoint(posX, posY)
                    pad = self.GetPad(False, pos)                    
                pad.SetPadName(self.GetName(x,y))
                self.AddPad(pad)

class WSONWizard(HFPW.HelpfulFootprintWizardPlugin):
    pad_num_pads_key = 'pads count'
    pad_width_key = 'pad width'
    pad_length_key = 'pad length'
    pad_first_length_key = 'first pad length'
    pad_pitch_key = 'pad pitch'
    pad_row_spacing_key = 'row spacing'
    pad_handsolder_key = 'hand solder margin'

    body_width_key = 'width'
    body_length_key = 'length'
    body_x_margin_key = 'x margin'
    body_y_margin_key = 'y margin'
    
    def GetName(self):
        return "WSON"

    def GetDescription(self):
        return "WSON footprint wizard"

    def GetValue(self):
        return "WSON"

    def GenerateParameterList(self):
        self.AddParam("Pads", self.pad_num_pads_key, self.uNatural, 6)
        self.AddParam("Pads", self.pad_width_key, self.uMM, 0.28)
        self.AddParam("Pads", self.pad_length_key, self.uMM, 0.75)
        self.AddParam("Pads", self.pad_first_length_key, self.uMM, 0.85)
        self.AddParam("Pads", self.pad_pitch_key, self.uMM, 0.5)
        self.AddParam("Pads", self.pad_row_spacing_key, self.uMM, 1.15)
        self.AddParam("Pads", self.pad_handsolder_key, self.uMM, 0)
        
        self.AddParam("Body", self.body_width_key, self.uMM, 1.55)
        self.AddParam("Body", self.body_length_key, self.uMM, 1.55)
        self.AddParam("Body", self.body_x_margin_key, self.uMM, 0.1)
        self.AddParam("Body", self.body_y_margin_key, self.uMM, 0.1)

    def CheckParameters(self):
        self.CheckParamInt(
            "Pads", '*' + self.pad_num_pads_key,
            is_multiple_of=2)
    

    def GetFirstPad(self):
        pad_length = self.parameters["Pads"][self.pad_first_length_key]
        pad_width = self.parameters["Pads"][self.pad_width_key]
        pad_handsolder = self.parameters["Pads"][self.pad_handsolder_key]
        
        pad_length_hansolder = pad_length+pad_handsolder
        return PA.PadMaker(self.module).SMDPad(
            pad_length_hansolder, pad_width, 
            shape=pcbnew.PAD_SHAPE_RECT)

    def GetPad(self):
        pad_length = self.parameters["Pads"][self.pad_length_key]
        pad_width = self.parameters["Pads"][self.pad_width_key]
        pad_handsolder = self.parameters["Pads"][self.pad_handsolder_key]
        
        pad_length_hansolder = pad_length+pad_handsolder
        return PA.PadMaker(self.module).SMDPad(
            pad_length_hansolder, pad_width, 
            shape=pcbnew.PAD_SHAPE_RECT)

    def BuildThisFootprint(self):

        pads = self.parameters["Pads"]
        body = self.parameters["Body"]
        
        pad_num_pads = pads['*'+self.pad_num_pads_key] 
        pad_width = pads[self.pad_width_key]
        pad_length = pads[self.pad_length_key]
        pad_first_length = pads[self.pad_first_length_key]
        pad_pitch = pads[self.pad_pitch_key]
        pad_row_spacing = pads[self.pad_row_spacing_key]
        pad_handsolder = pads[self.pad_handsolder_key]
        
        body_width = body[self.body_width_key]
        body_length = body[self.body_length_key]
        body_x_margin = body[self.body_x_margin_key]
        body_y_margin = body[self.body_y_margin_key]
        
        # add in the pads
        first_pad = self.GetFirstPad()
        pad = self.GetPad()
        pad_row_spacing_handsolder = pad_row_spacing+pad_handsolder
        array = WSONGridArray(first_pad, pad_first_length-pad_length, pad, pad_num_pads/2, 2, pad_pitch, pad_row_spacing_handsolder)
        array.AddPadsToModule(self.draw)

        # draw silk screen
        ssx = body_length+body_x_margin*2
        ssy = body_width+body_y_margin*2
        self.draw.Box(0, 0, ssx, ssy)

        # Courtyard
        self.draw.SetLayer(pcbnew.F_CrtYd)
        self.draw.Box(0, 0, ssx, ssy)

        #reference and value
        text_size = self.GetTextSize()  # IPC nominal
        self.draw.Value(0, -ssy/2-text_size, text_size)
        self.draw.Reference(0, ssy/2+text_size, text_size)

        
WSONWizard().register()
