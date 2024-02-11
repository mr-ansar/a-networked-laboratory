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
'''Run a test #3 (see better-auto-lab/analysis.py).

This 3nd version of the analysis.py module passes the management of multiple
network connections to the GroupTable object. This is the same as the
second version.

In addition this version asks the connection manager to start an object
at that moment when all the required connections are in place. Rather
than processing a stream of messages (i.e. GroupUpdate and Ready) to
detect the proper moment to begin processing, a CreateFrame is passed
to the manager. At that moment of readiness that frame is used to create
the object and the group of address is inserted as the first argument.

This completely separates the application code from all connection-
related details. The analysis() function shrinks to a bare minimum. Note
that the initial gathering of connections from test #2 is no longer
needed, as is the ongoing checks for loss of connections. At the same
time, as long as it honours the Stop() protocol, the process remains
responsive to all possibilities (broken networks and crashing services)
and always terminates with the most relevant information.

Refer to best-auto-lab/analysis.py for the final implementation.
'''
import ansar.connect as ar
from interface.db_if import *
from interface.temperature_if import *
from interface.strain_if import *

# Where are the contributing services?
class Settings(object):
	def __init__(self, temperature_ipp=None, strain_ipp=None, db_ipp=None, name=None, span=None):
		self.temperature_ipp = temperature_ipp or ar.HostPort()
		self.strain_ipp = strain_ipp or ar.HostPort()
		self.db_ipp = db_ipp or ar.HostPort()
		self.name = name
		self.span = span

SETTINGS_SCHEMA = {
	'temperature_ipp': ar.UserDefined(ar.HostPort),
	'strain_ipp': ar.UserDefined(ar.HostPort),
	'db_ipp': ar.UserDefined(ar.HostPort),
	'name': ar.Unicode(),
	'span': ar.TimeSpan(),
}

ar.bind(Settings, object_schema=SETTINGS_SCHEMA)


#
#
def analysis(self, group, name, span):
	# Good to go.
	# Verify the use of name with the db.
	m = self.ask(OpenFrame(name), (ar.Ack, ar.Nak, ar.Stop), group.db)
	if isinstance(m, ar.Ack):
		pass
	elif isinstance(m, ar.Nak):
		return m
	else:
		return ar.Aborted()

	# Move to the collection phase.
	if span:
		self.start(ar.T1, span)
	self.start(ar.T2, 1.0, repeating=True)

	started = ar.world_now()
	sample = ar.deque()

	while True:
		m = self.select(ar.T1, ar.T2, TemperatureSample, StrainEdge, ar.Stop)
		if isinstance(m, ar.T1):
			break
		elif isinstance(m, ar.T2):
			self.send(ar.Enquiry(), group.temperature)
		elif isinstance(m, TemperatureSample):
			s = DeviceSample(device='temperature', stamp=ar.world_now(), value=m.temperature)
			sample.append(s)
		elif isinstance(m, StrainEdge):
			s = DeviceSample(device='strain', stamp=ar.world_now(), value=m.strain)
			sample.append(s)
		else:
			return ar.Aborted()

	# Sample period over.
	ended = ar.world_now()
	delta = ended - started

	frame = SampleFrame(name=name,
		started=started,
		ended=ended,
		seconds=delta.total_seconds(),
		sample=sample)

	self.send(frame, group.db)
	self.select(ar.Ack, seconds=3.0)

	return frame

ar.bind(analysis)

#
#
READY_OR_NOT = 120.0

def settings_to_args(settings):
	group = ar.GroupTable(
		temperature=ar.CreateFrame(ar.ConnectToAddress, settings.temperature_ipp),
		strain=ar.CreateFrame(ar.ConnectToAddress, settings.strain_ipp),
		db=ar.CreateFrame(ar.ConnectToAddress, settings.db_ipp),
	)
	return group, (settings.name, settings.span), {}

# Initialize settings and start the main object.
factory_settings = Settings(temperature_ipp=ar.HostPort(host='127.0.0.1', port=6011),
	strain_ipp=ar.HostPort(host='127.0.0.1', port=6012),
	db_ipp=ar.HostPort(host='127.0.0.1', port=6013),
	name='test',
	span=30.0)

if __name__ == '__main__':
	ar.create_object(ar.GroupObject, settings_to_args, analysis, get_ready=READY_OR_NOT, factory_settings=factory_settings)
