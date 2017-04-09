#!/bin/bash

sudo cp -f pcbnew/python/plugins/*.py /usr/share/kicad/scripting/plugins/
sudo rm -f /usr/share/kicad/scripting/plugins/*.pyc

echo "KiCad should now be restarted to use new plugins"  