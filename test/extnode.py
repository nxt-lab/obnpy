import sys
sys.path.append('../src')
from obnpy.obnnode import *
import numpy as num


def main():
	# create node
	node = OBNNode('extnode','testext','tcp://localhost:1883')
	

	# create the ports
	node.udouble = node.create_input('input_scalardouble','scalar','double')
	node.ydouble = node.create_output('output_scalardouble','scalar','double')

	node.uvector = node.create_input('input_vectordouble','vector','double')
	node.yvector = node.create_output('output_vectordouble', 'vector','double')

	node.umatrix = node.create_input('input_matrixdouble','matrix','double')
	node.ymatrix = node.create_output('output_matrixdouble', 'matrix','double')
	# callbacks

	MAINBLOCK = 0
	node.d = 1.0
	node.v = num.array([2.1, 0.9],num.dtype('double'))
	node.m = num.array([[1.0, 2.0],[3.0, 4.0]],num.dtype('double'))
	node.x = 0.0

	node.on_init(initcallback)
	node.on_term(termcallback)
	#on_block_output(node, function, blkid, *args, **kwargs):
	node.on_block_output(blockoutput,MAINBLOCK,node,MAINBLOCK)
	node.on_block_state(blockstate,MAINBLOCK,node)

	print("Ready to start simulation...")
	status = node.run(20)
	print("Final status: ", status)

def termcallback():
		print("TERM")

def initcallback():
		print("INIT")

def blockoutput(node,MAINBLOCK):
		print("Current time is "+ str(node.sim_time())+ "s.")
	  	#println("Current time is ", wallclock_time(node))
	  	print("Scalar double: "+ str(node.udouble.get()) )
	  	#print("Scalar double: "+ str(node.input_ports['input_scalardouble'].get())
	  	node.ydouble.set(node.d)
	  	node.d += 1

	  	node.yvector.set(node.v)
	  	node.v += num.ones(2)

	  	node.ymatrix.set(node.m)
	  	node.m += num.eye(2)

	  	node.schedule(node.update_mask(MAINBLOCK),node.sim_time()+0.5, 1 ,'s')

def blockstate(node):
		node.x += node.udouble.get()
		print("double: " + str(node.x))
		print("vector : ")
		print node.uvector.get()
		print("matrix : ")
		print node.umatrix.get()

if __name__ == '__main__':
	main()




