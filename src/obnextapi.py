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

# Node Interface

# Create a new node object, given nodeName, workspace, and optional server address.
# Returns 0 if successful; >0 if node already exists; <0 if error.
# id stores the ID of the new node.
# int createOBNNode(const char* name, const char* workspace, const char* server, size_t* id);

lib.createOBNNode.argtypes = [c_char_p, c_char_p, c_char_p, POINTER(c_size_t)]
lib.createOBNNode.restype = c_int

lib.deleteOBNNode.argtypes = [c_size_t]
lib.deleteOBNNode.restype = c_int