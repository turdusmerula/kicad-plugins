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


class RTCWizard(HFPW.HelpfulFootprintWizardPlugin):
    pad_width_key = 'pad width'
    pad_length_key = 'pad length'
    pad_pitch_key = 'pad pitch'
    pad_handsolder_key = 'hand solder margin'

    body_width_key = 'width'
    body_length_key = 'length'
    body_x_margin_key = 'x margin'
    body_y_margin_key = 'y margin'
    
    def GetName(self):
        return "RTC"

    def GetDescription(self):
        return "Discrete 2 pins RTC wizard"

    def GetValue(self):
        return "RTC"

    def GenerateParameterList(self):
        self.AddParam("Pads", self.pad_width_key, self.uMM, 0.5)
        self.AddParam("Pads", self.pad_length_key, self.uMM, 1.25)
        self.AddParam("Pads", self.pad_pitch_key, self.uMM, 1.5)
        self.AddParam("Pads", self.pad_handsolder_key, self.uMM, 0)
        
        self.AddParam("Body", self.body_width_key, self.uMM, 1.25)
        self.AddParam("Body", self.body_length_key, self.uMM, 2)
        self.AddParam("Body", self.body_x_margin_key, self.uMM, 0.1)
        self.AddParam("Body", self.body_y_margin_key, self.uMM, 0.1)

    def CheckParameters(self):
        None
    

    def GetPad(self):
        pad_length = self.parameters["Pads"][self.pad_length_key]
        pad_width = self.parameters["Pads"][self.pad_width_key]
        pad_handsolder = self.parameters["Pads"][self.pad_handsolder_key]
        
        pad_width_hansolder = pad_width+pad_handsolder
        return PA.PadMaker(self.module).SMDPad(
            pad_length, pad_width_hansolder, 
            shape=pcbnew.PAD_SHAPE_RECT)

    def BuildThisFootprint(self):

        pads = self.parameters["Pads"]
        body = self.parameters["Body"]
        
        pad_width = pads[self.pad_width_key]
        pad_length = pads[self.pad_length_key]
        pad_pitch = pads[self.pad_pitch_key]
        pad_handsolder = pads[self.pad_handsolder_key]
        
        body_width = body[self.body_width_key]
        body_length = body[self.body_length_key]
        body_x_margin = body[self.body_x_margin_key]
        body_y_margin = body[self.body_y_margin_key]
        
        # add in the pads
        pad = self.GetPad()
        pad_pitch_handolder = pad_pitch+pad_handsolder
        array = PA.PadGridArray(pad, 2, 1, pad_pitch_handolder, 0)
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

        
RTCWizard().register()
