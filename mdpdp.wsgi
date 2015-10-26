#!/usr/bin/python

import sys
import logging
logging.basicConfig(stream=sys.stderr)


activate_this = '/home/ikko/repo/mdpdp/startweb.py'
sys.path.insert(0,"/home/ikko/repo/mdpdp/")

from startweb import app as application
# application.run()
# import startweb
# execfile(activate_this, dict(__file__=activate_this))