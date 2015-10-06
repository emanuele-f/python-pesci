#!/bin/env python2
# -*- coding: utf-8 -*-
#
# Emanuele Faranda                         <black.silver@hotmail.it>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#

class SyntaxError(Exception):
    def __init__(self, node, line, column):
        self.node = node
        self.line = line
        self.column = column

    def __str__(self):
        return "Bad syntax at line %d:%d : node '%s'" % (
            self.line,
            self.column,
            self.node.__class__.__name__ )

class RuntimeError(Exception):
    def __init__(self, cause):
        self.cause = cause

    def __str__(self):
        return "Runtime Error: %s " % self.cause

## Environment
class EnvVarNotFound(Exception):
    def __init__(self, env, vid):
        self.env = env
        self.vid = vid
    def __str__(self):
        return "Variable '%s' not found in environment %s" % (self.vid, self.env)

class EnvFuncNotFound(Exception):
    def __init__(self, env, vid):
        self.env = env
        self.vid = vid
    def __str__(self):
        return "Function '%s' not found in environment %s" % (self.vid, self.env)

class EnvSymbolNotFound(Exception):
    def __init__(self, env, vid):
        self.env = env
        self.vid = vid
    def __str__(self):
        return "Symbol '%s' not found in environment %s" % (self.vid, self.env)

class EnvExecEnd(Exception):
    def __init__(self, env):
        self.env = env

    def __str__(self):
        return "Execution has ended for environment %s" % self.env

class EnvContextsEmpty(Exception):
    def __init__(self, env):
        self.env = env
    def __str__(self):
        return "No context in environment '%s'" % (self.vid, self.env)

class EnvBadSymbolName(Exception):
    def __init__(self, env, sid):
        self.env = env
        self.sid = sid
    def __str__(self):
        return "Bad symbol name: '%s' in environment '%s'" % (self.sid, self.env)

class BadFunctionCall(Exception):
    def __init__(self, func):
        self.func = func
    def __str__(self):
        return "Bad function call: '%s'" % self.func
