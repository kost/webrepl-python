#!/usr/bin/env python

import webrepl
repl=webrepl.Webrepl(**{'host':'192.168.4.1','port':8266,'password':'ulx3s','debug':True})
ver=repl.get_ver()
print(ver)

