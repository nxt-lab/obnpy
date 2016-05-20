#!/usr/bin/env python

from ctypes import *
from obnextapi import *
from warnings import *
from datetime import datetime
# check raising errors!!!!

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




class OBNNode(object):

	def __init__(self, name, workspace, server ):
		nodeid = c_size_t()
		result = lib.createOBNNode(name,workspace,server,byref(nodeid))
		if result != 0 :
			raise ValueError('OBN node could not be created',res)

		self.valid = True
		self.id = nodeid.value

		# add empty callback attributes
		self.block_output_cb = {}
		self.block_state_cb = {}
		self.init_cb = None
		self.term_cb = None



	def delete(self ):

		lib.deleteOBNNode(self.id)
		self.valid = False
		print("Node deleted")

	# set callbacks
	def on_block_output(self, function, blkid, *args, **kwargs):
		assert(node.valid), 'Node is not valid'
		assert(blkid > 0 and blkid <= max_blockid), "Invalid computation block ID."

		self.block_output_cb[blkid] = OBNCallback(function,*args,**kwargs)

	def on_state_output(self, function, blkid, *args, **kwargs):
		assert(node.valid), 'Node is not valid'
		assert(blkid > 0 and blkid <= max_blockid), "Invalid computation block ID."

		self.block_state_cb[blkid] = OBNCallback(function,*args,**kwargs)

	def on_init(self, function, *args, **kwargs):
		assert(node.valid), 'Node is not valid'

		self.init_cb = OBNCallback(function,*args,**kwargs)

	def on_term(self, function, *args, **kwargs):
		assert(node.valid), 'Node is not valid'

		self.term_cb = OBNCallback(function,*args,**kwargs)
	# callback execution
	def do_updatey(self,mask):
		for blkid, callback in self.block_output_cb:
			if mask == 0:
				break
			if (mask & (1 << blkid)) != 0:
				# If the id is in the mask, run the callback
				callback()
    			# ^  bitwise xor
    			mask ^= (1 << blkid) # reset that bit

	def do_updatex(self,mask):
		for blkid, callback in self.block_state_cb:
			if mask == 0:
				break
			if (mask & (1 << blkid)) != 0:
				# If the id is in the mask, run the callback
				callback()
				# ^  bitwise xor
				mask ^= (1 << blkid) # reset that bit

	# Run simulation
	# Returns: 1 if timeout; 2 if the simulation stopped properly; 3 if stopped with an error

	def run(self, timeout = -1.0, stopIfTimeout = True):
		assert(node.valid), 'Node is not valid'

		event_type = c_uint()
		event_args = OBNEI_EventArg()

		result = 0

		while result == 0:
			result = lib.simRunStep(node.id, timeout, byref(event_type), byref(event_args))

			if result == 0:
				# there is an event
				if event_type == OBNEI_Event_Y:
					self.do_updatey(event_args.mask)
				elif event_type == OBNEI_Event_X:
					self.do_updatex(event_args.mask)
				elif event_type == OBNEI_Event_INIT:
					self.init_cb()
				elif event_type == OBNEI_Event_TERM:
					self.term_cb()
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

	def stop(self, stopnow = False):
		assert(node.valid), 'Node is not valid'

		if stopnow:
			result = lib.nodeStopSimulation(self.id)
		else:
			result = lib.nodeRequestStopSimulation(self.id)

		return (result == 0)

	# Requests a triggering (i.e., update) of certain blocks at a future time.
	# Returns the status of the request:
	# 0 if successful (accepted), -1 if timeout (failed), -2 if request is invalid, >0 if other errors (failed, see OBN documents for details).
	def schedule(self, blocks_mask, simtime, timeout = -1.0, *args):
		assert(node.valid), 'Node is not valid'
		# optional use
		# schedule(self, blocks_mask, simtime, timeunit, timeout, timeout)

		if args:
			# Here, the time is given in simulation time with a given unit (default = seconds) from the beginning of the simulation.
			# Valid units are :s, :m, :h, :ms, :us
			# This case converts the future time to the atomic clock ticks and call the default method
			atomictu = self.timeunit()
			timeunit = args[0]
			tu_scale = {'s':1e6, 'ms':1e3, 'us':1, 'm':60*1e6, 'h':60*60*1e6}
			# Convert t to clock ticks
			clkticks = simtime*tu_scale[timeunit] / atomictu
			self.schedule(blocks_mask, clkticks, timeout)
		elif type(simtime) is datetime:
				# Duration until the requested future time, in milliseconds
				# Here, the time is given in wallclock time.
				# This case converts the future time to the atomic clock ticks and call the default method
				dt = simtime - self.wallclock_time()
				assert(dt.total_seconds()>0), "Requested time must be strictly in the future."
				t = self.simtime('ms') + dt.total_seconds()*1e3
				self.schedule(blocks_mask, clkticks, timeout)
		else:
			# Here the time is in the clock ticks, i.e., the number of atomic time units from the beginning of the simulation.
			return lib.simRequestFutureUpdate(self.id, blocks_mask, simtime, timeout) 
		


	# Get current simulation time in given unit
	# Possible units as strings: us, ms, s, m, h
	def sim_time(self, unit = 's'):
		assert(node.valid), 'Node is not valid'
		# Time unit: 0 = second, -1 = millisecond, -2 = microsecond, 1 = minute, 2 = hour
		timeunits = {'s':0, 'ms':-1, 'us':-2, 'm':1, 'h':2}
		assert(unit in timeunits), 'Invalid time unit'

		curtime = c_double(0.0)
		result = lib.nodeSimulationTime(self.id, timeunits[unit], byref(curtime))
		if result != 0:
			raise ValueError("Error querying the simulation time [$result]: ")
		return curtime.value

	# Returns the atomic time unit as an integer in microseconds
	def timeunit(self):
		assert(node.valid), 'Node is not valid'

		tu = OBNSimTimeType(0)
		result = lib.nodeTimeUnit(node.id,byref(tu))
		if result != 0: raise ValueError("Error querying the time unit [$result]: ")
		return tu.value

	# Get current wallclock time as Python's DateTime
	def wallclock_time(self):
		assert(node.valid), 'Node is not valid'
		unixtime = c_longlong(0)
		result = lib.nodeWallClockTime(self.id, byref(unixtime))
		if result != 0:
			raise ValueError("Error querying the wall clock time [$result]: ")

		# needs testing
		return datetime.fromtimestamp(unixtime.value)

	# Internal function to check state of node
	def _is_state(self, apifun):
		assert(node.valid), 'Node is not valid'

		result = apifun(self.id)
		if result < 0 :  raise ValueError("Error querying node's state [$result]: ")
	# Check node's state
	def isstopped(self): return self._is_state(lib.nodeIsStopped)
	def isrunning(self): return self._is_state(lib.nodeIsRunning)
	def iserror(self): return self._is_state(lib.nodeIsError)
