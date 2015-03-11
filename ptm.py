#!/usr/bin/env python

import sys, re, fileinput, json

top = {'links':{}}

def dequote(s):
  if (s[0] == s[-1]) and s.startswith(("'", '"')):
    return s[1:-1]
  return s

l = 1
for line in fileinput.input(sys.argv[1:]):
  link = re.search('([\S]+):(\S+)\s*(--|->)\s*(\S+):([^\s;,]+)',line)
  if link:
    s1 = dequote(link.group(1))
    p1 = dequote(link.group(2))
    s2 = dequote(link.group(4))
    p2 = dequote(link.group(5))
    linkname = 'L%d' % (l)
    l += 1
    top['links'][linkname] = {'node1':s1,'port1':p1,'node2':s2,'port2':p2}

print json.dumps(top,sort_keys=True, indent=1)
