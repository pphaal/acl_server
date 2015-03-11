#!/usr/bin/env python

import sys, re, fileinput, json, requests

switch_list = ['leaf1','leaf2','spine1','spine2']

l = 0
linkdb = {}
links = {}
for switch_name in switch_list:
  # verify that lldp configuration exports hostname,ifname information
  r = requests.get("http://%s:8080/lldp/configuration" % (switch_name));
  if r.status_code != 200: continue
  config = r.json()
  lldp_hostname = config['configuration'][0]['config'][0]['hostname'][0]['value']
  if lldp_hostname != '(none)': continue
  lldp_porttype = config['configuration'][0]['config'][0]['lldp_portid-type'][0]['value']
  if lldp_porttype != 'ifname': continue
  # local hostname 
  r = requests.get("http://%s:8080/hostname" % (switch_name));
  if r.status_code != 200: continue
  host = r.json()
  # get neighbors
  r = requests.get("http://%s:8080/lldp/neighbors" % (switch_name));
  if r.status_code != 200: continue
  neighbors = r.json()
  interfaces = neighbors['lldp'][0]['interface']
  for i in interfaces:
    # local port name
    port = i['name']
    # neighboring hostname
    nhost = i['chassis'][0]['name'][0]['value']
    # neighboring port name
    nport = i['port'][0]['descr'][0]['value']
    if not host or not port or not nhost or not nport: continue
    if host < nhost:
      link = {'node1':host,'port1':port,'node2':nhost,'port2':nport}
    else:
      link = {'node1':nhost,'port1':nport,'node2':host,'port2':port}
    keystr = "%s %s -- %s %s" % (link['node1'],link['port1'],link['node2'],link['port2'])
    if keystr in linkdb:
       # check consistency
       prev = linkdb[keystr]
       if (link['node1'] != prev['node1'] 
           or link['port1'] != prev['port1']
           or link['node2'] != prev['node2']
           or link['port2'] != prev['port2']): raise Exception('Mismatched LLDP', keystr)
    else:
       linkdb[keystr] = link
       linkname = 'L%d' % (l)
       links[linkname] = link
       l += 1

top = {'links':links}               
print json.dumps(top,sort_keys=True, indent=1)
