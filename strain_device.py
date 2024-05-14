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
import uuid
import ansar.connect as ar
from strain_if import *
from wandering_float import *

#
#
def strain_device(self):
	metric = 'strain'
	style = 'async'
	unique = uuid.uuid4()
	name = f'device-{metric}-{style}-{unique}'

	delivered = {}		# Remember clients.

	ar.publish(self, name)
	m = self.select(ar.Published, ar.NotPublished, ar.Stop)
	if isinstance(m, ar.NotPublished):
		return m
	elif isinstance(m, ar.Stop):
		return ar.Aborted()

	a = self.create(wandering_float, 100.0, -100.0, self.address)
	while True:
		m = self.select(Wandering, ar.Delivered, ar.Cleared, ar.Dropped, ar.Stop)
		if isinstance(m, Wandering):
			pass
		elif isinstance(m, ar.Delivered):
			delivered[self.return_address] = m
			continue
		elif isinstance(m, (ar.Cleared, ar.Dropped)):
			delivered.pop(self.return_address)
			continue
		else:
			self.send(ar.Stop(), a)
			m = self.select(ar.Completed, ar.Stop)
			ar.retract(self)
			return ar.Aborted()

		# Convert the simulation value to a strain value and
		# broadcast to the current set of clients.
		edge = StrainEdge(m.value)
		for d in delivered.keys():
			self.send(edge, d)

ar.bind(strain_device)

#
#
if __name__ == '__main__':
	ar.create_node(strain_device)
