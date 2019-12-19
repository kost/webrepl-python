#!/usr/bin/env python

import webrepl
repl=webrepl.Webrepl(**{'host':'192.168.4.1','port':8266,'password':'ulx3s'})
resp=repl.sendcmd("import os; os.listdir()")
print(resp.decode("ascii"))


