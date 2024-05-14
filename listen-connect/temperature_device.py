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
'''A wandering floating-point value between HI and LO, and a network interface.

This is crude simulation of a sensor - some real-world value that might be measured
by electronic circuitry and delivered to the computing world as a floating point
value, e.g. in weather stations, lab equipment and manufacturing plants.

The primary purpose of this module is to demonstrate the interfacing beween
an async computing environment and a sync (poll-based) device, i.e. there is
a "blocking" aspect to the interaction. That "blocking" behaviour might occur
behind a 3rd-party library. Here that is simulated with the get_reading()
function.

For an example of async interfacing, refer to the strain_device.py module.
'''
import random
import ansar.connect as ar
from interface.temperature_if import Settings
from interface.temperature_if import TemperatureSample

random.seed()

# The simulated value.
temperature = 0.0

# The blocking interface.
def get_reading():
	global temperature
	return temperature

# Operational limits and support.
HI = 50.0
LO = -50.0
DOWN_UP= (-1.0, 1.0)

# The device object that provides a messaging interface around the sync
# API (i.e. get_reading).
class INITIAL: pass
class RUNNING: pass

class TemperatureDevice(ar.Point, ar.StateMachine):
	def __init__(self, group):
		ar.Point.__init__(self)
		ar.StateMachine.__init__(self, INITIAL)
		self.group = group

def TemperatureDevice_INITIAL_Start(self, message):
	self.start(ar.T1, 0.5, repeating=True)				# Start the wandering value.
	return RUNNING

def TemperatureDevice_RUNNING_T1(self, message):		# Make it look alive.
	global temperature

	# Around 2/5 of the time - no change.
	z = random.randrange(5)
	if z % 2 == 1:
		return RUNNING

	s = random.randrange(2)				# Sign.
	d = random.random() * DOWN_UP[s]	# Delta.
	c = temperature						# Current.
	t = c + d
	if t < LO or t > HI:		# Out of bounds.	
		temperature = c - d		# Go the other way.
	else:
		temperature = t
	self.console(f'Temperature [{temperature}]')
	return RUNNING

def TemperatureDevice_RUNNING_Enquiry(self, message):
	# Sync access.
	temperature = get_reading()

	# Respond with the sample.
	self.reply(TemperatureSample(temperature))
	return RUNNING

def TemperatureDevice_RUNNING_Stop(self, message):
	self.cancel(ar.T1)
	self.complete(ar.Aborted())

TEMPERATURE_DEVICE_DISPATCH = {
	INITIAL: (
		(ar.Start,), ()
	),
	RUNNING: (
		(ar.T1, ar.Enquiry, ar.Stop), ()
	),
}

ar.bind(TemperatureDevice, TEMPERATURE_DEVICE_DISPATCH)

# Describe the resources that are expected by the
# TemperatureDevice instance.
def group_args(settings):
	group = ar.GroupTable(
		server=ar.CreateFrame(ar.ListenAtAddress, settings.listening_ipp)
	)
	args = ()
	kw = {}

	return group, args, kw

# Executable entry point.
# Create a GroupObject that prepares the resources as described
# in table() and then runs an instance of TemperatureDevice.
factory_settings = Settings(ar.HostPort('127.0.0.1', 6011))

if __name__ == '__main__':
	ar.create_object(ar.GroupObject, TemperatureDevice, group_args, factory_settings=factory_settings)
