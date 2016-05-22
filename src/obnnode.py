#!/usr/bin/env python

from ctypes import *
from obnextapi import *
from warnings import *
from datetime import datetime
from weakref import *
import pdb
# check raising errors!!!!
# hide some attributes like ids

# a callback keeps a function handle and a tuple of custom arguments and keyword agruments
##usage 
# def foo(*args): print sum(args)
# fcallb = Callback(foo,1,2,3)
# fcall() 
class OBNCallback(object):
	def __init__(self, function, *args, **kwargs):
		self.function = function
		self.args = args
		self.kwargs = kwargs

	def __call__(self):
		# call function with optional arguments and keyword arguments
		self.function(*self.args, **self.kwargs)


class OBNPort(object):

	def __init__(port, node, portid, name, portType, container, elementType):
		port.node = proxy(node) # not a copy but a proxy to the parent node
		port.id = portid
		port.name = name
		port.type = portType
		port.container = container
		port.elementType = elementType
		port.valid = True

	def input(port):

		if port.container == 'scalar':

			if port.element == 'double':
				val = c_double()
				result = lib.inputScalarDoubleGet(port.node.id, port.id, byref(val))
			elif port.element == 'bool':
				val = c_bool()
				result = lib.inputScalarBoolGet(port.node.id, port.id, byref(val))
			elif port.element == 'int32':
				val = c_int()
				result = lib.inputScalarInt32Get(port.node.id, port.id, byref(val))
			elif port.element == 'int64':
				val = c_longlong()
				result = lib.inputScalarInt64Get(port.node.id, port.id, byref(val))
			elif port.element == 'uint32':
				val = c_uint()
				result = lib.inputScalarUInt32Get(port.node.id, port.id, byref(val))
			elif port.element == 'uint64':
				val = c_ulonglong()
				result = lib.inputScalarUInt64Get(port.node.id, port.id, byref(val))

		return val.value

	def output(port,val):

		if port.container == 'scalar':

			if port.element == 'double':
				val = c_double()
				result = lib.outputScalarDoubleGet(port.node.id, port.id, val)
			elif port.element == 'bool':
				val = c_bool()
				result = lib.outputScalarBoolGet(port.node.id, port.id, val)
			elif port.element == 'int32':
				val = c_int()
				result = lib.outputScalarInt32Get(port.node.id, port.id, val)
			elif port.element == 'int64':
				val = c_longlong()
				result = lib.outputScalarInt64Get(port.node.id, port.id, val)
			elif port.element == 'uint32':
				val = c_uint()
				result = lib.outputScalarUInt32Get(port.node.id, port.id, val)
			elif port.element == 'uint64':
				val = c_ulonglong()
				result = lib.outputScalarUInt64Get(port.node.id, port.id, val)

		return val.value

	def portInfo(port):
		assert(port.node.valid), 'Node is not valid'
		pInfo = OBNEI_PortInfo()
		result = lib.portInfo(port.node.id, port.id, byref(pInfo))
		if result != 0: raise ValueError('Error getting port information',res)

		# retrieve the key with value matching the portinfo enumeration
		info = {}
		info['type'] = OBNEI_PortType.keys()[OBNEI_PortType.values().index(pInfo.type)]
		info['container'] = OBNEI_ContainerType.keys()[OBNEI_ContainerType.values().index(pInfo.container)]
		info['elementType'] = OBNEI_ElementType.keys()[OBNEI_ElementType.values().index(pInfo.elementType)]

		return info

	# Returns: 0 if successful, otherwise error ID (last error message contains the error message).
	def portConnect(port, srcPort):
		assert(port.node.valid), 'Node is not valid'
		result = lib.portConnect(port.node.id, port.id, srcPort)
		return result

class OBNNode(object):

	def __init__(node, name, workspace, server ):
		nodeid = c_size_t()
		result = lib.createOBNNode(name,workspace,server,byref(nodeid))
		if result != 0 :
			raise ValueError('OBN node could not be created',res)

		node.valid = True
		node.id = nodeid.value

		# add empty callback attributes
		node.block_output_cb = {}
		node.block_state_cb = {}
		node.init_cb = None
		node.term_cb = None

		# empty port dict
		node.ports = {'input':{} ,'output':{}}


	# write desctiption
	def create_port(node, portType, portName, containerType, elementType, strict = False, formatType = 'ProtoBuf'):
		assert(node.valid), 'Node is not valid'
		assert(containerType in OBNEI_ContainerType), "invalid container type, valid types: 'scalar' ,'vector', 'matrix', 'binary'"
		assert(elementType in OBNEI_ElementType), "invalid element type, valid types: 'logical', 'double', 'int32', 'int64', 'uint32', 'uint64'"
		assert(portType in OBNEI_PortType), "invalid port type, valid types: 'input', ''output, 'data'"


		if portType == 'input':
			portid = lib.createInputPort(node.id,
										 portName, 
										 OBNEI_FormatType[formatType],
										 OBNEI_ContainerType[containerType],
										 OBNEI_ElementType[elementType],
										 strict)
		elif portType == 'output':
			portid = lib.createOutputPort(node.id,
										 portName, 
										 OBNEI_FormatType[formatType],
										 OBNEI_ContainerType[containerType],
										 OBNEI_ElementType[elementType])

		if portid < 0: raise ValueError("Error creating input port [$result]: ")				
		else: node.ports[portType][portName] = OBNPort(node, portid, portName, portType, containerType, elementType)





	def delete(node ):

		lib.deleteOBNNode(node.id)
		node.valid = False
		print("Node deleted")

	# set callbacks
	def on_block_output(node, function, blkid, *args, **kwargs):
		assert(node.valid), 'Node is not valid'
		assert(blkid > 0 and blkid <= max_blockid), "Invalid computation block ID."

		node.block_output_cb[blkid] = OBNCallback(function,*args,**kwargs)

	def on_state_output(node, function, blkid, *args, **kwargs):
		assert(node.valid), 'Node is not valid'
		assert(blkid > 0 and blkid <= max_blockid), "Invalid computation block ID."

		node.block_state_cb[blkid] = OBNCallback(function,*args,**kwargs)

	def on_init(node, function, *args, **kwargs):
		assert(node.valid), 'Node is not valid'

		node.init_cb = OBNCallback(function,*args,**kwargs)

	def on_term(node, function, *args, **kwargs):
		assert(node.valid), 'Node is not valid'

		node.term_cb = OBNCallback(function,*args,**kwargs)
	# callback execution
	def do_updatey(node,mask):
		for blkid, callback in node.block_output_cb:
			if mask == 0:
				break
			if (mask & (1 << blkid)) != 0:
				# If the id is in the mask, run the callback
				callback()
    			# ^  bitwise xor
    			mask ^= (1 << blkid) # reset that bit

	def do_updatex(node,mask):
		for blkid, callback in node.block_state_cb:
			if mask == 0:
				break
			if (mask & (1 << blkid)) != 0:
				# If the id is in the mask, run the callback
				callback()
				# ^  bitwise xor
				mask ^= (1 << blkid) # reset that bit

	# Run simulation
	# Returns: 1 if timeout; 2 if the simulation stopped properly; 3 if stopped with an error

	def run(node, timeout = -1.0, stopIfTimeout = True):
		assert(node.valid), 'Node is not valid'

		event_type = c_uint()
		event_args = OBNEI_EventArg()

		result = 0

		while result == 0:
			result = lib.simRunStep(node.id, timeout, byref(event_type), byref(event_args))

			if result == 0:
				# there is an event
				if event_type == OBNEI_Event_Y:
					node.do_updatey(event_args.mask)
				elif event_type == OBNEI_Event_X:
					node.do_updatex(event_args.mask)
				elif event_type == OBNEI_Event_INIT:
					node.init_cb()
				elif event_type == OBNEI_Event_TERM:
					node.term_cb()
				# elif event_type == OBNEI_Event_RCV:
				# Port's RCV event
				else:
					raise ValueError("Internal error: Unknown event type.",event_type)
			elif result == 1:
				warn("Simulation has timed out.")
				if stopIfTimeout:
					print("I should be stopping the sim immediately")
			elif result == 2:
				print("I should be stopping properly")
			elif result == 3:
				warn("Simulation has stopped due to an error.")
			else:
				raise ValueError("Internal error: Unknown event type.",result)

		return result

	def stop(node, stopnow = False):
		assert(node.valid), 'Node is not valid'

		if stopnow:
			result = lib.nodeStopSimulation(node.id)
		else:
			result = lib.nodeRequestStopSimulation(node.id)

		return (result == 0)

	# Requests a triggering (i.e., update) of certain blocks at a future time.
	# Returns the status of the request:
	# 0 if successful (accepted), -1 if timeout (failed), -2 if request is invalid, >0 if other errors (failed, see OBN documents for details).
	def schedule(node, blocks_mask, simtime, timeout = -1.0, *args):
		assert(node.valid), 'Node is not valid'
		# optional use
		# schedule(node, blocks_mask, simtime, timeunit, timeout, timeout)

		if args:
			# Here, the time is given in simulation time with a given unit (default = seconds) from the beginning of the simulation.
			# Valid units are :s, :m, :h, :ms, :us
			# This case converts the future time to the atomic clock ticks and call the default method
			atomictu = node.timeunit()
			timeunit = args[0]
			tu_scale = {'s':1e6, 'ms':1e3, 'us':1, 'm':60*1e6, 'h':60*60*1e6}
			# Convert t to clock ticks
			clkticks = simtime*tu_scale[timeunit] / atomictu
			node.schedule(blocks_mask, clkticks, timeout)
		elif type(simtime) is datetime:
				# Duration until the requested future time, in milliseconds
				# Here, the time is given in wallclock time.
				# This case converts the future time to the atomic clock ticks and call the default method
				dt = simtime - node.wallclock_time()
				assert(dt.total_seconds()>0), "Requested time must be strictly in the future."
				t = node.simtime('ms') + dt.total_seconds()*1e3
				node.schedule(blocks_mask, clkticks, timeout)
		else:
			# Here the time is in the clock ticks, i.e., the number of atomic time units from the beginning of the simulation.
			return lib.simRequestFutureUpdate(node.id, blocks_mask, simtime, timeout) 
		


	# Get current simulation time in given unit
	# Possible units as strings: us, ms, s, m, h
	def sim_time(node, unit = 's'):
		assert(node.valid), 'Node is not valid'
		# Time unit: 0 = second, -1 = millisecond, -2 = microsecond, 1 = minute, 2 = hour
		timeunits = {'s':0, 'ms':-1, 'us':-2, 'm':1, 'h':2}
		assert(unit in timeunits), 'Invalid time unit'

		curtime = c_double(0.0)
		result = lib.nodeSimulationTime(node.id, timeunits[unit], byref(curtime))
		if result != 0:
			raise ValueError("Error querying the simulation time [$result]: ")
		return curtime.value

	# Returns the atomic time unit as an integer in microseconds
	def timeunit(node):
		assert(node.valid), 'Node is not valid'

		tu = OBNSimTimeType(0)
		result = lib.nodeTimeUnit(node.id,byref(tu))
		if result != 0: raise ValueError("Error querying the time unit [$result]: ")
		return tu.value

	# Get current wallclock time as Python's DateTime
	def wallclock_time(node):
		assert(node.valid), 'Node is not valid'
		unixtime = c_longlong(0)
		result = lib.nodeWallClockTime(node.id, byref(unixtime))
		if result != 0:
			raise ValueError("Error querying the wall clock time [$result]: ")

		# needs testing
		return datetime.fromtimestamp(unixtime.value)

	# Internal function to check state of node
	def _is_state(node, apifun):
		assert(node.valid), 'Node is not valid'

		result = apifun(node.id)
		if result < 0 :  raise ValueError("Error querying node's state [$result]: ")
	# Check node's state
	def isstopped(node): return node._is_state(lib.nodeIsStopped)
	def isrunning(node): return node._is_state(lib.nodeIsRunning)
	def iserror(node): return node._is_state(lib.nodeIsError)
