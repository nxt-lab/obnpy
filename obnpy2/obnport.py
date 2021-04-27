from ctypes import *
from obnextapi import *

class OBNNode(object):

	def __init__( self, name, workspace, server ):
		id = c_size_t()
		result = lib.createOBNNode(name,workspace,server,byref(id))
		if result != 0 :
			raise ValueError('OBN node could not be created',res)

		self.id = id.value


	def delete( self ):

		lib.deleteOBNNode(self.id)
		print("Node deleted")