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
'''
import random
import ansar.connect as ar

__all__ = [
	'Wandering',
	'get_wandering',
	'wandering_float',
]

# Edge event.
class Wandering(object):
	def __init__(self, value=None):
		self.value = value

ar.bind(Wandering, object_schema={'value': ar.Float8()})

# The changing value.
float_value = 0.0

# Blocking interface for polling clients.
def get_wandering():
	global float_value
	return float_value

random.seed()
DOWN_UP= (-1.0, 1.0)

# Thread to modify the value over time.
def wandering_float(self, high, low, client=None):
	global float_value

	seconds = random.random() * 5.0		
	self.start(ar.T1, seconds)

	while True:
		m = self.select(ar.T1, ar.Stop)
		if isinstance(m, ar.T1):
			pass
		else:
			return ar.Aborted()			# Control-c.

		# Fabricate a change of float_value.
		s = random.randrange(2)				# Up or down.
		d = random.random() * DOWN_UP[s]	# Delta.
		c = float_value						# Current.
		t = c + d
		if t < low or t > high:		# Keep it in range.
			float_value = c - d		# Invert.
		else:
			float_value = t

		if client:
			self.send(Wandering(float_value), client)

		seconds = random.random() * 5.0		
		self.start(ar.T1, seconds)

ar.bind(wandering_float)
