#!/usr/bin/env python
import os
from ctypes import *
import glob

# QUESTIONS
# NO REF TO MQTT OR YARP ? HOW TO SPECIFY ?


libpath = os.path.abspath(os.path.join(os.path.dirname(__file__), 'libobnext-mqtt.*'))
lib = cdll.LoadLibrary(glob.glob(libpath)[0])

# declare ctypes argument and return types
# refer to: https://docs.python.org/2/library/ctypes.html




# /** The update mask type is uint64_t, see obnsim_basic.h for the definition. That should match the definition here. */
# /** Type to pass arguments of an event */
OBNUpdateMask = c_ulonglong
OBNSimTimeType = c_longlong

class OBNEI_EventArg(Structure):
    _fields_ = [("mask", OBNUpdateMask),
                ("index", c_size_t)]

#/** The event types */
# might require a cast
OBNEI_Event_INIT = 0        # Init of simulation
OBNEI_Event_Y = 1          # Update Y
OBNEI_Event_X = 2            # Update X
OBNEI_Event_TERM = 3         # Termination of simulation
OBNEI_Event_RCV = 4           # A port has received a message


# =====  Node Interface  =====


# Create a new node object, given nodeName, workspace, and optional server address.
# Returns 0 if successful; >0 if node already exists; <0 if error.
# id stores the ID of the new node.
# int createOBNNode(const char* name, const char* workspace, const char* server, size_t* id);

lib.createOBNNode.argtypes = [c_char_p, c_char_p, c_char_p, POINTER(c_size_t)]
lib.createOBNNode.restype = c_int

 #   // Delete a node, given its ID
 #   // Returns 0 if successful; <0 if node doesn't exist.
 #   int deleteOBNNode(size_t id);

lib.deleteOBNNode.argtypes = [c_size_t]
lib.deleteOBNNode.restype = c_int


 #   // Request/notify the SMN to stop, then terminate the node's simulation regardless of whether the request was accepted or not. See MQTTNodeExt::stopSimulation for details.
 #   // Args: node ID
 #   // Return: 0 if successful
 #   int nodeStopSimulation(size_t nodeid);

lib.nodeStopSimulation.argtypes = [c_size_t]
lib.nodeStopSimulation.restype = c_int


 #   // Requests the SMN/GC to stop the simulation (by sending a request message to the SMN) but does not terminate the node.
 #   // If the SMN/GC accepts the request, it will broadcast a TERM message to all nodes, which in turn will terminate this node.
 #   // See MQTTNodeExt::requestStopSimulation() for details.
 #   // Args: node ID
 #   // Return: 0 if successful
 #   int nodeRequestStopSimulation(size_t nodeid);

lib.nodeRequestStopSimulation.argtypes = [c_size_t]
lib.nodeRequestStopSimulation.restype = c_int

 #   // Check if the current state of the node is STOPPED
 #   // Args: node ID
 #   // Returns: true if >0, false if =0, error if <0.
 #   int nodeIsStopped(size_t nodeid);

lib.nodeIsStopped.argtypes = [c_size_t]
lib.nodeIsStopped.restype = c_int

 #   // Check if the current state of the node is ERROR
 #   // Args: node ID
 #   // Returns: true if >0, false if =0, error if <0.
 #   int nodeIsError(size_t nodeid);

lib.nodeIsError.argtypes = [c_size_t]
lib.nodeIsError.restype = c_int

 #   // Check if the current state of the node is RUNNING
 #   // Args: node ID
 #   // Returns: true if >0, false if =0, error if <0.
 #   int nodeIsRunning(size_t nodeid);

lib.nodeIsRunning.argtypes = [c_size_t]
lib.nodeIsRunning.restype = c_int

#	// Returns the current simulation time of the node with a desired time unit.
#    // Args: node ID, the time unit, double* time
#    // Returns: 0 if successful
#    // *time receives the current simulation time as a double (real number)
#    // The time unit is an integer specifying the desired time unit. The allowed values are:
#    // 0 = second, -1 = millisecond, -2 = microsecond, 1 = minute, 2 = hour
#    int nodeSimulationTime(size_t nodeid, int timeunit, double* T);
    
lib.nodeSimulationTime.argtypes = [c_size_t, c_int, POINTER(c_double)]
lib.nodeSimulationTime.restype = c_int

#    // Returns the atomic time unit, an integer in microseconds, of the simulation.
#    // Args: node ID, OBNSimTimeType* tu
#    // Returns: 0 if successful
#    int nodeTimeUnit(size_t nodeid, OBNSimTimeType* tu);

lib.nodeTimeUnit.argtypes = [c_size_t, POINTER(OBNSimTimeType)]
lib.nodeTimeUnit.restype = c_int

#    // Returns the current wallclock time of the node.
#    // Args: node ID, long* time
#    // Returns: 0 if successful
#    // *time receives the current wallclock time as a POSIX time value.
#    int nodeWallClockTime(size_t nodeid, int64_t* T);

lib.nodeWallClockTime.argtypes = [c_size_t, c_int, POINTER(c_longlong)]
lib.nodeWallClockTime.restype = c_int

#    /* === Node simulation control interface === */

#    // Get the next port event (e.g. message received) with a possible timeout.
#    // Args: node ID, timeout (double in seconds, can be <= 0.0 if no timeout, i.e. returns immediately), unsigned int* event_type, size_t* portID
#    // Returns: 0 if successful, >0 if timeout, <0 if other errors
#    // If returning 0: *event_type is the type of port event (an integer cast from OBNEI_EventType, OBNEI_Event_RCV for message received); *portID is the index of the port associated with the event.
#    int simGetPortEvent(size_t nodeid, double timeout, unsigned int* event_type, size_t* portid);

lib.simGetPortEvent.argtypes = [c_size_t, c_double, POINTER(c_uint), POINTER(c_size_t)]
lib.simGetPortEvent.restype = c_int


#	// Runs the node's simulation until the next event, or until the node stops or has errors
#    // Args: node ID, timeout (double in seconds, can be <= 0.0 if no timeout), unsigned int* event_type, OBNEI_EventArg* event_args
#    // Returns: 0 if everything is going well and there is an event pending, 1 if timeout (but the simulation won't stop automatically, it's still running), 2 if the simulation has stopped (properly, not because of an error), 3 if the simulation has stopped due to an error (the node's state becomes NODE_ERROR), <0 if other error (e.g., node ID is invalid).  Check the last error message for specifics.
#    // If returning 0: *event_type is the type of port event (an integer cast from OBNEI_EventType); *event_args are the event arguments depending on the event type (see the structure for details).
#    int simRunStep(size_t nodeid, double timeout, unsigned int* event_type, OBNEI_EventArg* event_args);

lib.simRunStep.argtypes = [c_size_t, c_double, POINTER(c_uint), c_void_p]
lib.simRunStep.restype = c_int


#    // Request an irregular future update.
#    // This is a blocking call, possibly with a timeout, that waits until it receives the response from the SMN or until a timeout.
#    // Args: node ID, future time (integer value in the future), update mask of the requested update, timeout (double, can be <= 0)
#    // Returns: status of the request: 0 if successful (accepted), -1 if timeout (failed), -2 if request is invalid, >0 if other errors (failed, see OBN documents for details).
#    int simRequestFutureUpdate(size_t nodeid, OBNSimTimeType t, OBNUpdateMask mask, double timeout);

lib.simRequestFutureUpdate.argtypes = [c_size_t, OBNSimTimeType, OBNUpdateMask, c_double]
lib.simRequestFutureUpdate.restype = c_int


#api_nodeIsStopped = c_void_p.in_dll(lib, "nodeIsStopped")
#api_nodeIsError = c_void_p.in_dll(lib, "nodeIsError")
#api_nodeIsRunning = c_void_p.in_dll(lib, "nodeIsRunning")
# =====  Port Interface  =====


#    /* === Misc === */
#    // Returns the maximum ID allowed for an update type.
#    int maxUpdateID();

lib.maxUpdateID.argtypes = []
lib.maxUpdateID.restype = c_int

max_blockid = lib.maxUpdateID()


