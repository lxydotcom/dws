#!/usr/bin/env python

import os, sys, shutil

# The base image's conf has defined [include] section, just copy customized conf to including directory
script_path = sys.argv[0]
script_loc = "/".join(script_path.split('/')[:-1])
customizedConf = "%s/supervisord.conf" % (script_loc)

dirPath = "/etc/supervisor/conf.d/"
if not os.path.exists(dirPath):
    os.makedirs(dirPath)

shutil.copy2(customizedConf, dirPath)

print "Customized supervisord.conf has been added"
