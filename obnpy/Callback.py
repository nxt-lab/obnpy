#!/usr/bin/env python

# a callback keeps a function handle and a tuple of custom arguments and keyword agruments
##usage 
# def foo(*args): print sum(args)
# fcallb = Callback(foo,1,2,3)
# fcall() 
class Callback(object):
	def __init__(self, function, *args, **kwargs):
		self.function = function
		self.args = args
		self.kwargs = kwargs

	def __call__(self):
		# call function with optional arguments and keyword arguments
		self.function(*self.args, **self.kwargs)






