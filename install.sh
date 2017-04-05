#!/bin/bash

sudo cp -f pcbnew/python/plugins/*.py /usr/share/kicad/scripting/plugins/

echo "KiCad should now be restarted to use new plugins"  