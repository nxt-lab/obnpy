#!/usr/bin/env python

from obnport import OBNNode

name = 'newnode'
workspace 'powernet'
server = 'tcp://localhost:1883'
a = OBNNode('node1','ws','tcp://localhost:1883')
a.delete()

