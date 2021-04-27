import os
from ctypes import *
from ctypes.util import find_library
import glob
import sys
import numpy as num
from numpy.ctypeslib import ndpointer
# QUESTIONS
# NO REF TO MQTT OR YARP ? HOW TO SPECIFY ?


#### Load dynamic library for the obn node c interface #####
## find local library
#libpath = os.path.abspath(os.path.join(os.path.dirname(__file__), 'libobnext-mqtt.*'))
#lib = cdll.LoadLibrary(glob.glob(libpath)[0])

# do first on MAC : add to ~/.bash_profile the following line
#export DYLD_LIBRARY_PATH=$DYLD_LIBRARY_PATH:$OBN_DIR/nodecpp/build

# load dynamic library with correct extension according to the OS
if sys.platform == "linux" or sys.platform == "linux2":
    lib = CDLL('libobnext-mqtt.so') # linux
elif sys.platform == "darwin":
    lib = CDLL('libobnext-mqtt.dylib')# OS X
elif sys.platform == "win32":
    lib = CDLL('libobnext-mqtt.dll')# Windows...

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




 # PORT INTERFACE

OBNEI_PortType = {'input': 0, 'output': 1, 'data':2}
OBNEI_ContainerType = {'scalar':0 ,'vector':1, 'matrix':2, 'binary':3 } 
OBNEI_ElementType = {'bool': 0, 'double': 1, 'int32':2, 'int64':3, 'uint32': 4, 'uint64':5}
OBNEI_FormatType = {'ProtoBuf': 0} 
#
#	// Create a new input port on a node
#    // Arguments: node ID, port's name, format type, container type, element type, strict or not
#    // Returns port's id; or negative number if error.
#    // id is an integer starting from 0.
 # int createInputPort(size_t id,
 #                        const char* name,
 #                        OBNEI_FormatType format,
 #                        OBNEI_ContainerType container,
 #                        OBNEI_ElementType element,
 #                        bool strict);
lib.createInputPort.argtypes = [c_size_t, c_char_p, c_uint, c_uint, c_uint, c_bool]

    # // Create a new output port on a node
    # // Arguments: node ID, port's name, format type, container type, element type
    # // Returns port's id; or negative number if error.
    # // id is an integer starting from 0.
    # int createOutputPort(size_t id,
    #                      const char* name,
    #                      OBNEI_FormatType format,
    #                      OBNEI_ContainerType container,
    #                      OBNEI_ElementType element);

lib.createOutputPort.argtypes = [c_size_t, c_char_p, c_uint, c_uint, c_uint]








#             if port.elementType == 'double':
#                 val = c_double()
#                 result = lib.inputScalarDoubleGet(port.node.id, port.id, byref(val))
#             elif port.elementType == 'bool':
#                 val = c_bool()
#                 result = lib.inputScalarBoolGet(port.node.id, port.id, byref(val))
#             elif port.elementType == 'int32':
#                 val = c_int()
#                 result = lib.inputScalarInt32Get(port.node.id, port.id, byref(val))
#             elif port.elementType == 'int64':
#                 val = c_longlong()
#                 result = lib.inputScalarInt64Get(port.node.id, port.id, byref(val))
#             elif port.elementType == 'uint32':
#                 val = c_uint()
#                 result = lib.inputScalarUInt32Get(port.node.id, port.id, byref(val))
#             elif port.elementType == 'uint64':
#                 val = c_ulonglong()
#                 result = lib.inputScalarUInt64Get(port.node.id, port.id, byref(val))


ctypesdict = {'double':c_double,'bool':c_bool,'int32':c_int, 'int64':c_longlong, 'uint32': c_uint, 'uint64': c_ulonglong}
#numtypesdict = {'double':num.double,'bool':num.bool,'int32':num.int32, 'int64':num.int64, 'uint32': num.uint32, 'uint64': num.uint64}

 #   /** These functions read the current value of a non-strict scalar input port, or pop the top/front value of a strict scalar input port.
 #    Args: node ID, port's ID, pointer to scalar variable to receive the value.
 #    Returns: 0 if successful; <0 if error; >0 if no value actually read (e.g., no pending value on a strict port).
 #    For strict ports, if there is no value pending, the receiving variable won't be changed and the function will return 1.
 #    */
 #   int inputScalarDoubleGet(size_t nodeid, size_t portid, double* pval);      // Float64
lib.inputScalarDoubleGet.argtypes = [c_size_t, c_size_t, POINTER(c_double)]
 #   int inputScalarBoolGet(size_t nodeid, size_t portid, bool* pval);          // C++ bool (1 byte)
lib.inputScalarBoolGet.argtypes = [c_size_t, c_size_t, POINTER(c_bool)]
 #   int inputScalarInt32Get(size_t nodeid, size_t portid, int32_t* pval);      // Int32
lib.inputScalarInt32Get.argtypes = [c_size_t, c_size_t, POINTER(c_int)]
 #   int inputScalarInt64Get(size_t nodeid, size_t portid, int64_t* pval);      // Int64
lib.inputScalarInt64Get.argtypes = [c_size_t, c_size_t, POINTER(c_longlong)]
 #   int inputScalarUInt32Get(size_t nodeid, size_t portid, uint32_t* pval);    // UInt32
lib.inputScalarUInt32Get.argtypes = [c_size_t, c_size_t, POINTER(c_uint)]
 #   int inputScalarUInt64Get(size_t nodeid, size_t portid, uint64_t* pval);    // UInt64
lib.inputScalarUInt64Get.argtypes = [c_size_t, c_size_t, POINTER(c_ulonglong)]

inputScalarGet = {}
inputScalarGet['double'] = lib.inputScalarDoubleGet
inputScalarGet['bool']   = lib.inputScalarBoolGet
inputScalarGet['int32']  = lib.inputScalarInt32Get
inputScalarGet['int64']  = lib.inputScalarInt64Get
inputScalarGet['uint32'] = lib.inputScalarUInt32Get
inputScalarGet['uint64'] = lib.inputScalarUInt64Get


 #   /** These functions set the value of a scalar output port, but does not send it immediately.
 #    Usually the value will be sent out at the end of the event callback (UPDATE_Y).
 #    Args: node ID, port's ID, scalar value.
 #    Returns: 0 if successful; <0 if error
 #    */
 #   int outputScalarDoubleSet(size_t nodeid, size_t portid, double val);      // Float64
lib.outputScalarDoubleSet.argtypes = [c_size_t, c_size_t, c_double]
 #   int outputScalarBoolSet(size_t nodeid, size_t portid, bool val);          // C++ bool (1 byte)
lib.outputScalarBoolSet.argtypes = [c_size_t, c_size_t, c_bool]
 #   int outputScalarInt32Set(size_t nodeid, size_t portid, int32_t val);      // Int32
lib.outputScalarInt32Set.argtypes = [c_size_t, c_size_t, c_int]
 #   int outputScalarInt64Set(size_t nodeid, size_t portid, int64_t val);      // Int64
lib.outputScalarInt64Set.argtypes = [c_size_t, c_size_t, c_longlong]
 #   int outputScalarUInt32Set(size_t nodeid, size_t portid, uint32_t val);    // UInt32
lib.outputScalarUInt32Set.argtypes = [c_size_t, c_size_t, c_uint]
 #   int outputScalarUInt64Set(size_t nodeid, size_t portid, uint64_t val);    // UInt64
lib.outputScalarUInt64Set.argtypes = [c_size_t, c_size_t, c_ulonglong]


# create dictionary of function handles for different element types
outputScalarSet = {}
outputScalarSet['double'] = lib.outputScalarDoubleSet
outputScalarSet['bool']   = lib.outputScalarBoolSet
outputScalarSet['int32']  = lib.outputScalarInt32Set
outputScalarSet['int64']  = lib.outputScalarInt64Set
outputScalarSet['uint32'] = lib.outputScalarUInt32Set
outputScalarSet['uint64'] = lib.outputScalarUInt64Set


# === GET FUNCTIONS === #

# VECTORS

    # /** These functions read (or pop) the value from a non-strict (or strict) vector/matrix input port.
    #  For each port, there are two functions: *Get and *Release.
    #  - The *Get(nodeid, portid, void** pMan, <elem-type>** pVals, size_t* nrows, size_t* ncols) [for vector version, there is no ncols] gets the array of values and put its pointer to pVals (if pVals = NULL this won't be done) and also returns its dimensions (nrows, ncols) as well as a management object in pMan.  It is critical that pMan is received and used later on because it will be used to release the memory used in C.
    #  - *Release(void* pMan, <elem-type>* pBuf) copies the values to buffer pBuf if pBuf is not nill, then releases the management object.  When a port is read by *Get, it may allocate temporary memory and may be locked (so that new incoming messages will not override the current value).  It's CRITICALLY IMPORTANT to call *Release on the returned management object to release the memory and the lock on the port.  The copying is optional, only if pBuf is valid, which must be allocated by the external language.  This can be used instead of copying the data from pVals to the buffer in the external language (e.g., if pVals in *Get is NULL or ignored).

    #  There are two ways to use the returned values:
    #  - The safest way is to copy the values to a vector / matrix managed by the external language, via pVals returned by *Get or via pBuf in *Release.
    #  - The values in pVals can also be used directly BUT MUST NOT BE CHANGED (i.e., they are constant) and *Release MUST BE CALLED after this is done.  For example if we simply want to take the sum of the elements, this can be the most efficient way.  However, note that between *Get and *Release, the port is usually locked, hence whatever operations are done on the values should be quick.  Another use case could be to access some elements to decide if we want to use the values in further calculation, in that case we can copy the values over, otherwise we just ignore them.

    #  Function *Get(...) returns 0 if successful, <0 if error; >0 if no value actually read (e.g., no pending value on a strict port).
    #  For strict ports, if there is no value pending, the receiving variables won't be changed and the function will return 1, and there is no need to call *Release (obviously).  In other words, only call *Release if *Get returns 0.
    #  */
    # int inputVectorDoubleGet(size_t nodeid, size_t portid, void** pMan, const double** pVals, size_t* nelems);      // Float64
    # void inputVectorDoubleRelease(void* pMan, double* pBuf);

#lib.inputVectorDoubleGet.argtypes = [c_size_t, c_size_t, POINTER(c_void_p), POINTER(ndpointer(c_double)) ,POINTER(c_size_t) ]
#lib.inputVectorDoubleGet.argtypes = [c_size_t, c_size_t, POINTER(c_void_p), ndpointer(c_double) ,POINTER(c_size_t) ]
#lib.inputVectorDoubleRelease.argtypes = [c_void_p, ndpointer(c_double)]

lib.inputVectorDoubleGet.argtypes = [c_size_t, c_size_t, POINTER(c_void_p), POINTER(POINTER(c_double)),POINTER(c_size_t) ]
lib.inputVectorDoubleRelease.argtypes = [c_void_p, POINTER(c_double)]


inputVectorGet = {}
inputVectorGet['double'] = lib.inputVectorDoubleGet
inputVectorGet['bool']   = lib.inputVectorBoolGet
inputVectorGet['int32']  = lib.inputVectorInt32Get
inputVectorGet['int64']  = lib.inputVectorInt64Get
inputVectorGet['uint32'] = lib.inputVectorUInt32Get
inputVectorGet['uint64'] = lib.inputVectorUInt64Get

inputVectorRelease = {}
inputVectorRelease['double'] = lib.inputVectorDoubleRelease
inputVectorRelease['bool']   = lib.inputVectorBoolRelease
inputVectorRelease['int32']  = lib.inputVectorInt32Release
inputVectorRelease['int64']  = lib.inputVectorInt64Release
inputVectorRelease['uint32'] = lib.inputVectorUInt32Release
inputVectorRelease['uint64'] = lib.inputVectorUInt64Release

# MATRIX

 #   int inputMatrixDoubleGet(size_t nodeid, size_t portid, void** pMan, const double** pVals, size_t* nrows, size_t* ncols);      // Float64
#    void inputMatrixDoubleRelease(void* pMan, double* pBuf);

lib.inputMatrixDoubleGet.argtypes = [c_size_t, c_size_t, POINTER(c_void_p), POINTER(POINTER(c_double)),POINTER(c_size_t) ,POINTER(c_size_t) ]
lib.inputMatrixDoubleRelease.argtypes = [c_void_p, POINTER(c_double)]

inputMatrixGet = {}
inputMatrixGet['double'] = lib.inputMatrixDoubleGet
inputMatrixGet['bool']   = lib.inputMatrixBoolGet
inputMatrixGet['int32']  = lib.inputMatrixInt32Get
inputMatrixGet['int64']  = lib.inputMatrixInt64Get
inputMatrixGet['uint32'] = lib.inputMatrixUInt32Get
inputMatrixGet['uint64'] = lib.inputMatrixUInt64Get

inputMatrixRelease = {}
inputMatrixRelease['double'] = lib.inputMatrixDoubleRelease
inputMatrixRelease['bool']   = lib.inputMatrixBoolRelease
inputMatrixRelease['int32']  = lib.inputMatrixInt32Release
inputMatrixRelease['int64']  = lib.inputMatrixInt64Release
inputMatrixRelease['uint32'] = lib.inputMatrixUInt32Release
inputMatrixRelease['uint64'] = lib.inputMatrixUInt64Release


# ==== SET FUNCTIONS ===== #


    # /** These functions set the vector/matrix value of a vector/matrix output port, but does not send it immediately.
    #  Usually the value will be sent out at the end of the event callback (UPDATE_Y).
    #  The data are copied over to the port's internal memory, so there is no need to maintain the array pval after calling these functions (i.e., the caller is free to deallocate the memory of pval).
    #  Args: node ID, port's ID, <elem-type>* source, size_t nrows, size_t ncols  (for vector: size_t nelems)
    #  Returns: 0 if successful; <0 if error
    #  */

# VECTOR

    # int outputVectorDoubleSet(size_t nodeid, size_t portid, const double* pval, size_t nelems);      // Float64

#lib.outputVectorDoubleSet.argtypes = [c_size_t, c_size_t, ndpointer(c_double), c_size_t]
lib.outputVectorDoubleSet.argtypes = [c_size_t, c_size_t, POINTER(c_double), c_size_t]
#lib.outputVectorDoubleSet.argtypes = [c_size_t, c_size_t, POINTER(ndpointer(c_double)), c_size_t]
outputVectorSet = {}
outputVectorSet['double'] = lib.outputVectorDoubleSet
outputVectorSet['bool']   = lib.outputVectorBoolSet
outputVectorSet['int32']  = lib.outputVectorInt32Set
outputVectorSet['int64']  = lib.outputVectorInt64Set
outputVectorSet['uint32'] = lib.outputVectorUInt32Set
outputVectorSet['uint64'] = lib.outputVectorUInt64Set

# MATRIX

lib.outputMatrixDoubleSet.argtypes = [c_size_t, c_size_t, POINTER(c_double), c_size_t, c_size_t]




outputMatrixSet = {}
outputMatrixSet['double'] = lib.outputMatrixDoubleSet
outputMatrixSet['bool']   = lib.outputMatrixBoolSet
outputMatrixSet['int32']  = lib.outputMatrixInt32Set
outputMatrixSet['int64']  = lib.outputMatrixInt64Set
outputMatrixSet['uint32'] = lib.outputMatrixUInt32Set
outputMatrixSet['uint64'] = lib.outputMatrixUInt64Set











#    // Synchronous sending: request an output port to send its current value/message immediately and wait until it can be sent.
#    // Note that this function does not accept a value to be sent; instead the value/message of the port is set by another function.
#    // Args: node ID, port's ID
#    // Returns: zero if successful
#    // This function will return an error if the given port is not a physical output port.
#    int outputSendSync(size_t nodeid, size_t portid);

lib.outputSendSync.argtypes = [c_size_t, c_size_t]



    # // Is there a value pending at an input port?
    # // Args: node ID, port's ID
    # // Returns: true if >0, false if =0, error if <0.
    # int inputPending(size_t nodeid, size_t portid);

lib.inputPending.argtypes = [c_size_t, c_size_t]





class OBNEI_PortInfo(Structure):
    _fields_ = [("type", c_uint),
                ("container", c_uint),
                ("elementType", c_uint)]
 #   // Returns information about a port.
 #   // Arguments: node ID, port's ID, pointer to an OBNEI_PortInfo structure to receive info
 #   // Returns: 0 if successful.
 #   int portInfo(size_t nodeid, size_t portid, OBNEI_PortInfo* pInfo);

lib.portInfo.argtypes = [c_size_t, c_size_t, c_void_p]

    # // Request to connect a given port to a port on a node.
    # // Arguments: node ID, port's ID, source port's name (string)
    # // Returns: 0 if successful, otherwise error ID (last error message contains the error message).
    # int portConnect(size_t nodeid, size_t portid, const char* srcport);
lib.portConnect.argtypes = [c_size_t, c_size_t, c_char_p]

    # // Enables the message received event at an input port
    # // Args: node ID, port's ID
    # // Returns: 0 if successful
    # int portEnableRcvEvent(size_t nodeid, size_t portid);



# MISC

 #   // Returns the maximum ID allowed for an update type.
 #   int maxUpdateID();
#def max_blockid(): return lib.max_blockid()