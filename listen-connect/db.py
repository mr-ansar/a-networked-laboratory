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
'''A persistent store for monitoring results.

This module sets up a network listen at a configured address. Clients connect
to that address and query the db for context and also store the results of
monitoring sessions.
'''
import ansar.connect as ar
from interface.db_if import Settings
from interface.db_if import OpenFrame, SampleFrame

#
#
class INITIAL: pass
class RUNNING: pass

class Db(ar.Point, ar.StateMachine):
	def __init__(self, group):
		ar.Point.__init__(self)
		ar.StateMachine.__init__(self, INITIAL)
		self.group = group
		self.folder = None
		self.db = None

def Db_INITIAL_Start(self, message):
	m = ar.object_model_folder()
	if m is None:
		self.complete(ar.Faulted('folder "model" not found', 'nowhere for db'))

	kn = (lambda f: f.name, lambda f: f.name)

	self.folder = m.folder('db', te=ar.UserDefined(SampleFrame), keys_names=kn)
	self.db = {k: f for k, f, _ in self.folder.recover()}

	return RUNNING

def Db_RUNNING_OpenFrame(self, message):
	f = self.db.get(message.name, None)
	if f is not None:
		self.reply(ar.Nak())
		return RUNNING

	f = SampleFrame(name=message.name)
	self.folder.add(self.db, f)
	self.reply(ar.Ack())
	return RUNNING

def Db_RUNNING_SampleFrame(self, message):
	self.folder.update(self.db, message)
	self.reply(ar.Ack())
	return RUNNING

def Db_RUNNING_Stop(self, message):
	self.complete(ar.Aborted())

DB_DISPATCH = {
	INITIAL: (
		(ar.Start,), ()
	),
	RUNNING: (
		(OpenFrame, SampleFrame, ar.Stop), ()
	),
}

ar.bind(Db, DB_DISPATCH)

# Executable entry point.
# Create a GroupObject that uses group_args() to declare the
# resources (i.e. group) that must be ready before the Db instance
# is created. It also converts settings into arguments.
factory_settings = Settings(listening_ipp=ar.HostPort('127.0.0.1', 6013))

def group_args(settings):
	group = ar.GroupTable(
		server=ar.CreateFrame(ar.ListenAtAddress, settings.listening_ipp)
	)
	args = ()
	kw = {}

	return group, args, kw

if __name__ == '__main__':
	ar.create_object(ar.GroupObject, Db, group_args, factory_settings=factory_settings)
