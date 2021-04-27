#!/usr/bin/env python

from obnpy2.obnnode import *
import time
import pdb
import numpy as np

def main():

	print "======= SCALAR TEST ======="

	n1 = OBNNode('node1','ws','tcp://localhost:1883')

	n2 = OBNNode('node2','ws','tcp://localhost:1883')

	inportscalar = n1.create_input('inputport','scalar','double',strict = True)
	#n1.input_ports['inputport'].portInfo()
	outportscalar = n2.create_output('outputport','scalar','double',strict = True)

	res =  n1.input_ports['inputport'].portConnect('ws/node2/outputport')
	print res
	if res == 0: print('successful port connection')	

	getval = n1.input_ports['inputport'].get()


	print "sending data from node2/output to node1/output"
	val = 3
	#n2.output_ports['outputport'].set(val)
	#sendboolscalar = n2.output_ports['outputport'].sendsync()
	outportscalar.set(val)
	sendboolscalar = outportscalar.sendsync()
	print "sendbool is ",sendboolscalar 

	time.sleep(1)


	print "checking pending data at input port"
	#res = n1.input_ports['inputport'].pending()
	res = inportscalar.pending()
	print res
	print "reading data from n node1/output"
	
	#getval = n1.input_ports['inputport'].get()
	getval = inportscalar.get()
	print getval

	print "======= VECTOR TEST ======="

	# create ports
	n1.create_input('invecport','vector','int32',strict = False)
	n2.create_output('outvecport','vector','int32',strict = False)

	# connecting ports
	res =  n1.input_ports['invecport'].portConnect('ws/node2/outvecport')
	print res
	if res == 0: print('successful port connection')	

	# print("trying dry get on vector input port")
	# getval = n1.input_ports['invecport'].get()

	#while not n1.input_ports['invecport'].pending():

	print "no pending data at input port"

	print "sending vector from node2 to node1"
	invec = np.array([5.2,2.3,3.4,4.1,5.2])
	print invec
	n2.output_ports['outvecport'].set(invec)
	sendbool = n2.output_ports['outvecport'].sendsync()

	print "sendbool is ",sendbool 

	time.sleep(1)

		#pdb.set_trace()
	
	print "reading vector from n node1/output"
	getval = n1.input_ports['invecport'].get()
	print getval

	print "======= MATRIX TEST ======="

	# create ports
	n1.create_input('inmatport','matrix','bool',strict = False)
	n2.create_output('outmatport','matrix','bool',strict = False)

	# connecting ports
	res =  n1.input_ports['inmatport'].portConnect('ws/node2/outmatport')
	print res
	if res == 0: print('successful port connection')	

	# print("trying dry get on vector input port")
	# getval = n1.input_ports['inmatport'].get()

	#while not n1.input_ports['inmatport'].pending():

	print "no pending data at input port"

	print "sending vector from node2 to node1"
	inmat = np.array([[0.5,0],[4,5],[3.4, 2.1]],dtype = np.float64)
	print inmat
	n2.output_ports['outmatport'].set(inmat)
	sendbool = n2.output_ports['outmatport'].sendsync()

	print "sendbool is ",sendbool 

	time.sleep(1)

		#pdb.set_trace()
	
	print "reading vector from n node1/output"
	getval = n1.input_ports['inmatport'].get()
	print getval





	n1.delete()
	n2.delete()


if __name__ == '__main__':
	main()