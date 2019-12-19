webrepl
======
Python module to handle micropython websocket (WS) repl protocol (client side only). It is modified original implementation to automatize working with web repl.

Examples
========

Simple example to get output of command:
```
import webrepl
repl=webrepl.Webrepl(**{'host':'192.168.4.1','port':8266,'password':'ulx3s'})
resp=repl.sendcmd("import os; os.listdir()")
print(resp.decode("ascii"))
```

Example to get version of webrepl on device:
```
import webrepl
repl=webrepl.Webrepl(**{'host':'192.168.4.1','port':8266,'password':'ulx3s','debug':True})
ver=repl.get_ver()
print(ver)
```

Requirements
============

It should work with both python2 and python3 with simple pip commands:
```
pip install webrepl
```

webreplcmd examples
========

Few webreplcmd examples:
```

webreplcmd --host 192.168.4.1 --password ulx3s ls
webreplcmd --host 192.168.4.1 --password ulx3s get src-remote-file.txt dest-local-file.txt
webreplcmd --host 192.168.4.1 --password ulx3s -v get src-remote-file.txt dest-local-file.txt
webreplcmd --host 192.168.4.1 --password ulx3s put src-local-file.txt dest-remote-file.txt
webreplcmd --host 192.168.4.1 --password ulx3s -v put src-local-file.txt dest-remote-file.txt
webreplcmd --host 192.168.4.1 --password ulx3s cat main.py
webreplcmd --host 192.168.4.1 --password ulx3s cmd 'import os; os.listdir()'
webreplcmd --host 192.168.4.1 --password ulx3s rm uftpd.py
```

Note that you can also specify basic parameters using environment variables:
```
export webrepl_HOST=127.0.0.1
export webrepl_PASSWORD=ulx3s
export webrepl_PORT=8266
```

and then you can just specify command:
```
webreplcmd ls
```

All options are listed using --help:

```
webreplcmd --help
```

Requirements
============

It should work with both python2 and python3 with simple pip commands:
```
sudo apt-get update
sudo apt-get install -y python3 python3-pip
sudo pip3 install webrepl
```

Manual
======

```
usage: webreplcmd [-h] [--host HOST] [--port PORT] [--verbose] [--debug]
                    [--password PASSWORD] [--before BEFORE] [--cmd CMD]
                    [--after AFTER]
                    CMD [CMD ...]

webrepl - connect to websocket webrepl

positional arguments:
  CMD                   commands for repl

optional arguments:
  -h, --help            show this help message and exit
  --host HOST, -i HOST  Host to connect to
  --port PORT, -P PORT  Port to connect to
  --verbose, -v         Verbose information
  --debug, -d           Enable debugging messages
  --password PASSWORD, -p PASSWORD
                        Password used to connect to
  --before BEFORE, -B BEFORE
                        command to execute before
  --cmd CMD, -c CMD     command to execute
  --after AFTER, -A AFTER
                        command to execute after

webreplcmd --host 192.168.4.1 --password ulx3s ls
webreplcmd --host 192.168.4.1 --password ulx3s get src-remote-file.txt dest-local-file.txt
webreplcmd --host 192.168.4.1 --password ulx3s put src-local-file.txt dest-remote-file.txt
webreplcmd --host 192.168.4.1 --password ulx3s cat main.py
webreplcmd --host 192.168.4.1 --password ulx3s cmd 'import os; os.listdir()'
```
