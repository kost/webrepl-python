#!/usr/bin/env python
from __future__ import print_function
import sys
import os
import struct
try:
    import usocket as socket
except ImportError:
    import socket
import sys
try:
    import ubinascii as binascii
except:
    import binascii
try:
    import uhashlib as hashlib
except:
    import hashlib

# Define to 1 to use builtin "websocket" module of MicroPython
USE_BUILTIN_WEBSOCKET = 0
# Treat this remote directory as a root for file transfers
SANDBOX = ""
#SANDBOX = "/tmp/webrepl/"
DEBUG = 0

WEBREPL_REQ_S = "<2sBBQLH64s"
WEBREPL_PUT_FILE = 1
WEBREPL_GET_FILE = 2
WEBREPL_GET_VER  = 3


if USE_BUILTIN_WEBSOCKET:
    from websocket import websocket
else:
    class websocket:

        def __init__(self, s):
            self.s = s
            self.buf = b""
            self.debug = False

        def writetext(self, data):
            l = len(data)
            if l < 126:
                hdr = struct.pack(">BB", 0x81, l)
            else:
                hdr = struct.pack(">BBH", 0x81, 126, l)
            self.s.send(hdr)
            self.s.send(data)

        def write(self, data):
            l = len(data)
            if l < 126:
                # TODO: hardcoded "binary" type
                hdr = struct.pack(">BB", 0x82, l)
            else:
                hdr = struct.pack(">BBH", 0x82, 126, l)
            self.s.send(hdr)
            self.s.send(data)

        def recvexactly(self, sz):
            res = b""
            while sz:
                data = self.s.recv(sz)
                if not data:
                    break
                res += data
                sz -= len(data)
            return res

        def debugmsg(self, msg):
          if self.debug:
              print(msg)

        def read(self, size, text_ok=False, size_match=True):
            if not self.buf:
                while True:
                    hdr = self.recvexactly(2)
                    assert len(hdr) == 2
                    fl, sz = struct.unpack(">BB", hdr)
                    if sz == 126:
                        hdr = self.recvexactly(2)
                        assert len(hdr) == 2
                        (sz,) = struct.unpack(">H", hdr)
                    if fl == 0x82:
                        break
                    if text_ok and fl == 0x81:
                        break
                    self.debugmsg("[i] Got unexpected websocket record of type %x, skipping it" % fl)
                    while sz:
                        skip = self.s.recv(sz)
                        self.debugmsg("[i] Skip data: %s" % skip)
                        sz -= len(skip)
                data = self.recvexactly(sz)
                assert len(data) == sz
                self.buf = data

            d = self.buf[:size]
            self.buf = self.buf[size:]
            if size_match:
              assert len(d) == size, len(d)
            return d

        def ioctl(self, req, val):
            assert req == 9 and val == 2

class Webrepl:

  def __init__(self, **params):
    self.host = self.getkey(params,"host")
    self.port = self.getkey(params,"port")
    self.password = self.getkey(params,"password")
    self.debug = self.getkey(params,"debug")
    self.verbose = self.getkey(params,"verbose")
    self.noauto = self.getkey(params,"noauto")

    self.s=None
    self.ws=None

    self.connected=False

    if self.port == None:
      self.port = 8266

    if self.host != None and not self.noauto:
      self.connect(self.host, self.port)
    if self.password != None and self.ws != None and not self.noauto:
      self.login(self.password)

  def getkey(self, dict, key):
    if key in dict:
      return dict[key]
    return None

  def debugmsg(self, msg):
    if self.debug:
        print(msg)

  def client_handshake(self, sock):
      cl = sock.makefile("rwb", 0)
      cl.write(b"""\
GET / HTTP/1.1\r
Host: echo.websocket.org\r
Connection: Upgrade\r
Upgrade: websocket\r
Sec-WebSocket-Key: foo\r
\r
""")
      l = cl.readline()
  #    print(l)
      while 1:
          l = cl.readline()
          if l == b"\r\n":
              break
  #        sys.stdout.write(l)

  def connect(self, host, port):
    self.debugmsg("[d] connecting to %s %s" % (host,port))
    self.s = socket.socket()
    ai = socket.getaddrinfo(host, port)
    addr = ai[0][4]
    #self.debugmsg("connecting to adr %r" % addr)

    self.s.connect(addr)
    #s = s.makefile("rwb")
    self.debugmsg("[d] handshake")
    self.client_handshake(self.s)
    self.ws = websocket(self.s)
    self.ws.debug = self.debug

  def disconnect (self):
    if self.s != None:
      self.s.close()
    self.s = None
    self.ws = None

  def login(self, passwd):
    self.debugmsg("[d] login as %s" % passwd)
    while True:
        c = self.ws.read(1, text_ok=True)
        if c == b":":
            assert self.ws.read(1, text_ok=True) == b" "
            break
    self.ws.write(passwd.encode("utf-8") + b"\r")
    self.debugmsg("[d] login sent %s" % passwd)
    resp = self.ws.read(64, text_ok=True, size_match=False)
    # b'\r\nWebREPL connected\r\n>>> '
    # b'\r\nAccess denied\r\n'
    if b"WebREPL connected" in resp:
      self.connected=True
    self.debugmsg("[d] login resp %s" % resp)

  def sendcmd(self, cmd, size=1024):
    if not self.connected:
      return b""
    self.debugmsg("[d] sending cmd %s" % cmd)
    self.ws.writetext(cmd.encode("utf-8") + b"\r\n")
    self.debugmsg("[d] getting response")
    resp = self.read_cmd(size)
    self.debugmsg("[d] got response %s" % resp)
    return resp

  def read_cmd(self, size):
    resp=b''
    newline=False
    while True:
      r=self.ws.read(size, text_ok=True, size_match=False)
      # self.debugmsg("got %s %d" % (r, len(r)))
      if r == b'>>> ' and newline:
        break
      if r == b'\r\n':
        newline=True
      else:
        newline=False
      resp = resp + r
    return resp

  def read_resp(self):
    data = self.ws.read(4)
    sig, code = struct.unpack("<2sH", data)
    assert sig == b"WB"
    return code


  def send_req(self, op, sz=0, fname=b""):
    rec = struct.pack(WEBREPL_REQ_S, b"WA", op, 0, 0, sz, len(fname), fname)
    self.debugmsg("[d] Sent request %r %d" % (rec, len(rec)))
    self.ws.write(rec)

  def set_binary(self):
    # Set websocket to send data marked as "binary"
    self.ws.ioctl(9, 2)

  def get_ver(self):
    if self.connected:
      self.send_req(WEBREPL_GET_VER)
      d = self.ws.read(3)
      d = struct.unpack("<BBB", d)
      return d

  def put_file(self, local_file, remote_file):
    sz = os.stat(local_file)[6]
    dest_fname = (SANDBOX + remote_file).encode("utf-8")
    rec = struct.pack(WEBREPL_REQ_S, b"WA", WEBREPL_PUT_FILE, 0, 0, sz, len(dest_fname), dest_fname)
    self.debugmsg("[d] put file struct %r %d" % (rec, len(rec)))
    self.ws.write(rec[:10])
    self.ws.write(rec[10:])
    assert self.read_resp() == 0
    cnt = 0
    with open(local_file, "rb") as f:
        while True:
            if self.verbose:
              sys.stderr.write("[i] Sent %d of %d bytes\r" % (cnt, sz))
              sys.stderr.flush()
            buf = f.read(1024)
            if not buf:
                break
            self.ws.write(buf)
            cnt += len(buf)
    if self.verbose:
      sys.stderr.write("\n")
    assert self.read_resp() == 0

  def get_file_content(self, remote_file):
    content=b''
    src_fname = (SANDBOX + remote_file).encode("utf-8")
    rec = struct.pack(WEBREPL_REQ_S, b"WA", WEBREPL_GET_FILE, 0, 0, 0, len(src_fname), src_fname)
    self.debugmsg("[d] get file content struct %r %d" % (rec, len(rec)))
    self.ws.write(rec)
    assert self.read_resp() == 0
    cnt = 0
    while True:
        self.ws.write(b"\0")
        (sz,) = struct.unpack("<H", self.ws.read(2))
        if sz == 0:
            break
        while sz:
            buf = self.ws.read(sz)
            if not buf:
                raise OSError()
            cnt += len(buf)
            content = content + buf
            sz -= len(buf)
            if self.verbose:
              sys.stderr.write("[i] Received %d bytes\r" % cnt)
              sys.stderr.flush()
    if self.verbose:
      sys.stderr.write("\n")
    assert self.read_resp() == 0
    return content

  def get_file(self, remote_file, local_file):
    src_fname = (SANDBOX + remote_file).encode("utf-8")
    rec = struct.pack(WEBREPL_REQ_S, b"WA", WEBREPL_GET_FILE, 0, 0, 0, len(src_fname), src_fname)
    self.debugmsg("[d] get file struct %r %d" % (rec, len(rec)))
    self.ws.write(rec)
    assert self.read_resp() == 0
    with open(local_file, "wb") as f:
        cnt = 0
        while True:
            self.ws.write(b"\0")
            (sz,) = struct.unpack("<H", self.ws.read(2))
            if sz == 0:
                break
            while sz:
                buf = self.ws.read(sz)
                if not buf:
                    raise OSError()
                cnt += len(buf)
                f.write(buf)
                sz -= len(buf)
                if self.verbose:
                  sys.stderr.write("[i] Received %d bytes\r" % cnt)
                  sys.stderr.flush()
    if self.verbose:
      sys.stderr.write("\n")
    assert self.read_resp() == 0

