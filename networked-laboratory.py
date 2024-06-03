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
import ansar.connect as ar
from temperature_if import *
from strain_if import *

#
#
def networked_laboratory(self):
	device_search = r'device-[a-zA-Z]+-[a-zA-Z]+\+.*'

	ar.subscribe(self, device_search)
	m = self.select(ar.Subscribed, ar.Stop)
	if isinstance(m, ar.Stop):
		return ar.Aborted()

	polled = {}
	self.start(ar.T1, 2.0, repeating=True)
	while True:
		m = self.select(ar.T1,
			TemperatureSample, StrainEdge,
			ar.Available,
			ar.Cleared, ar.Dropped,
			ar.Stop)
		if isinstance(m, ar.T1):
			for a in polled.keys():
				self.send(ar.Enquiry(), a)
		elif isinstance(m, ar.Available):
			if 'polled' in m.matched_name:
				polled[self.return_address] = m.matched_name
		elif isinstance(m, (ar.Cleared, ar.Dropped)):
			polled.pop(self.return_address, None)
		elif isinstance(m, TemperatureSample):
			device = self.return_address[-1]
			self.sample(temperature=m.temperature, device=device)
		elif isinstance(m, StrainEdge):
			device = self.return_address[-1]
			self.sample(strain=m.strain, device=device)
		else:
			ar.retract(self)
			return ar.Aborted()
	

ar.bind(networked_laboratory)

#
#
if __name__ == '__main__':
	ar.create_node(networked_laboratory)
