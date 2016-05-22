#!/usr/bin/env python

from obnnode import *

def main():

	n1 = OBNNode('node1','ws','tcp://localhost:1883')
	n1.create_port('input','inputport','scalar','double')
	n1.ports['input']['inputport'].portInfo()
	n2 = OBNNode('node2','ws','tcp://localhost:1883')
	n2.create_port('output','outputport','scalar','double')
	res =  n1.ports['input']['inputport'].portConnect('ws/node2/outputport')
	print res
	if res == 0: print('successful port connection')

	n1.delete()
	n2.delete()


if __name__ == '__main__':
	main()