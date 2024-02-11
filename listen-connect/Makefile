# Author: Scott Woods <scott.18.ansar@gmail.com.com>
# MIT License
#
# Copyright (c) 2022
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

# This file is a copy of fsm-listen-connect/Makefile except it deals with
# the session implementation of client and server.

# Normal use;
# $ make clean build home
# $ make start
# $ make
# $ make
# $ ..
all: run

# Useful lists of file names relating to executables
#
EXECUTABLES := temperature_device strain_device db analysis
BUILD := $(EXECUTABLES:%=dist/%)
SPEC := $(EXECUTABLES:%=%.spec)

# Default rule to turn a python script into an executable.
#
dist/% : %.py
	pyinstaller --onefile --log-level ERROR -p . $<

dist/ansar-group:
	pyinstaller --onefile --log-level ERROR -p . `which ansar-group`

clean::
	-rm -rf build dist $(SPEC)

clean::
	-rm -rf __pycache__ interface/__pycache__

#
#
build:: $(BUILD)

#
#
home:
	ansar create
	ansar deploy dist
	ansar add temperature_device temperature
	ansar add strain_device strain
	ansar add db db
	ansar run --group-name=front-end --create-group
	ansar run --group-name=back-end --create-group

clean::
	-ansar --force destroy

# Initiate the backend.
start:
	ansar start temperature strain db --group-name=back-end

# Terminate the backend.
stop:
	ansar stop back-end

# Update the environment as required and
# execute the client within the current shell,
# i.e. directing all logging to stderr.
# The run should complete with the message
# received from the server in response to the
# clients request.
run: build
	echo nothing yet

#@ansar --debug-level=DEBUG run temperature --group-name=back-end
