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
'''Interface for db.'''

import ansar.connect as ar

# Configuration.
class Settings(object):
	def __init__(self, listening_ipp=None):
		self.listening_ipp = listening_ipp or ar.HostPort()

SETTINGS_SCHEMA = {
	'listening_ipp': ar.UserDefined(ar.HostPort),
}

ar.bind(Settings, object_schema=SETTINGS_SCHEMA)

# Messages
class OpenFrame(object):
	def __init__(self, name=None):
		self.name = name

OPEN_FRAME_SCHEMA = {
	'name': ar.Unicode,
}

ar.bind(OpenFrame, object_schema=OPEN_FRAME_SCHEMA)

#
#
class DeviceSample(object):
	def __init__(self, device=None, stamp=None, value=None):
		self.device = device
		self.stamp = stamp
		self.value = value

DEVICE_SAMPLE_SCHEMA = {
	'device': ar.Unicode(),
	'stamp': ar.WorldTime(),
	'value': ar.Float8(),
}

ar.bind(DeviceSample, object_schema=DEVICE_SAMPLE_SCHEMA)

#
#
class SampleFrame(object):
	def __init__(self, name=None, started=None, ended=None, seconds=None, sample=None):
		self.name = name
		self.started = started
		self.ended = ended
		self.seconds = seconds
		self.sample = sample or ar.default_deque()

SAMPLE_FRAME_SCHEMA = {
	'name': ar.Unicode(),
	'started': ar.WorldTime(),
	'ended': ar.WorldTime(),
	'seconds': ar.TimeSpan(),
	'sample': ar.DequeOf(ar.UserDefined(DeviceSample)),
}

ar.bind(SampleFrame, object_schema=SAMPLE_FRAME_SCHEMA)
