# Author: Scott Woods <scott.18.ansar@gmail.com>
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
import uuid
import ansar.connect as ar
from temperature_if import *
from wandering_float import *

#
#
def temperature_device(self):
	metric = 'temperature'
	style = 'polled'
	unique = uuid.uuid4()
	name = f'device-{metric}-{style}+{unique}'

	ar.publish(self, name)
	m = self.select(ar.Published, ar.NotPublished, ar.Stop)
	if isinstance(m, ar.NotPublished):
		return m
	elif isinstance(m, ar.Stop):
		return ar.Aborted()

	a = self.create(wandering_float, 50.0, -50.0)
	while True:
		m = self.select(ar.Enquiry, ar.Stop)
		if isinstance(m, ar.Enquiry):
			pass
		else:
			self.send(ar.Stop(), a)
			m = self.select(ar.Completed, ar.Stop)
			ar.retract(self)
			return ar.Aborted()

		# Call the blocking interface to the simulation
		# and reply to the poll.
		temperature = get_wandering()
		self.reply(TemperatureSample(temperature))

ar.bind(temperature_device)

#
#
if __name__ == '__main__':
	ar.create_node(temperature_device)
