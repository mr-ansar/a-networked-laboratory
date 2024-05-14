# Author: Scott Woods <scott.18.ansar@gmail.com.com>
# MIT License
#
# Copyright (c) 2017-2024 Scott Woods
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
'''.
.
'''
import random
import ansar.connect as ar
from interface.strain_if import Settings
from interface.strain_if import StrainSample, StrainEdge

random.seed()

# A combined controller-session server object.
# Manipulates a wandering floaating point value.
# Accepts connections from clients.
# Broadcasts changes to all connected clients.
class INITIAL: pass
class STARTING: pass
class RUNNING: pass
class SESSION: pass

HI = 100.0
LO = -100.0
DOWN_UP= (-1.0, 1.0)

#
#
class StrainDevice(ar.Point, ar.StateMachine):
	def __init__(self, group):
		ar.Point.__init__(self)
		ar.StateMachine.__init__(self, INITIAL)
		self.group = group
		self.accepted = {}
		self.strain = 0.0

def StrainDevice_INITIAL_Start(self, message):
	seconds = random.random() * 5.0			# Next event in somewhere between 0.0 and 4.999 seconds.
	self.start(ar.T1, seconds)
	return RUNNING

def StrainDevice_RUNNING_T1(self, message):
	s = random.randrange(2)				# Sign.
	d = random.random() * DOWN_UP[s]	# Delta.
	c = self.strain						# Current.
	t = c + d
	if t < LO or t > HI:
		self.strain = c - d		# Go the other way.
	else:
		self.strain = t
	self.console(f'Strain [{self.strain}]')

	# Broadcast the event to the current
	# set of clients.
	edge = StrainEdge(self.strain)
	for a in self.accepted.keys():
		self.send(edge, a)

	seconds = random.random() * 5.0		# Next one.
	self.start(ar.T1, seconds)
	return RUNNING

def StrainDevice_RUNNING_Accepted(self, message):
	t = ar.tof(message)
	self.console(f'Session <{t}> at {self.return_address}')
	self.accepted[self.return_address] = message

	sample = StrainSample(self.strain)
	self.reply(sample)
	return RUNNING

def StrainDevice_RUNNING_Abandoned(self, message):
	t = ar.tof(message)
	self.console(f'Session <{t}> at {self.return_address}')
	del self.accepted[self.return_address]
	return RUNNING

def StrainDevice_RUNNING_Closed(self, message):
	t = ar.tof(message)
	self.console(f'Session <{t}> at {self.return_address}')
	del self.accepted[self.return_address]
	return RUNNING

def StrainDevice_RUNNING_Stop(self, message):
	self.cancel(ar.T1)
	self.complete(ar.Aborted())

STRAIN_DEVICE_DISPATCH = {
	INITIAL: (
		(ar.Start,), ()
	),
	RUNNING: (
		(ar.T1, ar.Accepted, ar.Abandoned, ar.Closed, ar.Stop), ()
	),
}

ar.bind(StrainDevice, STRAIN_DEVICE_DISPATCH)

#
#
def group_args(settings):
	group = ar.GroupTable(
		server=ar.CreateFrame(ar.ListenAtAddress, settings.listening_ipp)
	)
	args = ()
	kw = {}

	return group, args, kw

#
#
factory_settings = Settings(listening_ipp=ar.HostPort('127.0.0.1', 6012))

if __name__ == '__main__':
	ar.create_object(ar.GroupObject, StrainDevice, group_args, factory_settings=factory_settings)
