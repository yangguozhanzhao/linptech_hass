#!/Users/yangzhan/Desktop/linptech_hass/venv/bin/python3

# -*- coding: utf-8 -*-
import re
import sys

from homeassistant.__main__ import main

if __name__ == '__main__':
    sys.argv[0] = re.sub(r'(-script\.pyw?|\.exe)?$', '', sys.argv[0])
    sys.argv.append('-c')
    sys.argv.append('config')
    sys.exit(main())
