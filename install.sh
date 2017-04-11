#!/bin/bash

xpl_path=$(cd -P -- "$(dirname -- "$0")" && pwd -P)

cd ${xpl_path}

sudo cp -f pcbnew/python/plugins/*.py /usr/share/kicad/scripting/plugins/
sudo rm -f /usr/share/kicad/scripting/plugins/*.pyc

sudo cp -f pcbmodule/pcbmodule /usr/local/bin
 
echo "KiCad should now be restarted to use new plugins"  