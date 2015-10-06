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

import ast
import pesci.code
from pesci.errors import *

class ExecutionEnvironment:
    def __init__(self):
        self.reset()

    def reset(self):
        self.code = None
        self.ip = -1
        self._contexts = []
        self._stack = []
        self.iterator = None

        # create global context
        self.push_context()

    def setup(self, code):
        self.code = code
        self.ip = 0
        self.iterator = None

    def setvar(self, vid, val):
        if vid and vid[0] == "_":
            raise EnvBadSymbolName(self, vid)
        self._set_in_context(self._get_context(vid), vid, val)

    def getvar(self, vid):
        # Try to get defined function or name
        try:
            var = self._get_from_contexts(vid)
        except KeyError:
            raise EnvSymbolNotFound(self, vid)
        return var

    """set multiple k->v at one """
    def loadvars(self, vdict):
        for k,v in vdict.items():
            self.setvar(k, v)

    def _set_in_context(self, context, key, val):
        context[key] = val

    def _get_from_contexts(self, key):
        # search a key in the context stack
        for context in reversed(self._contexts):
            if context.has_key(key):
                return context[key]
        raise KeyError(key)

    """push a value into the call stack"""
    def push(self, val):
        self._stack.append(val)

    def pop(self):
        return self._stack.pop()

    def popall(self):
        s = self._stack
        self._stack = []
        return s

    """context: additional names pool"""
    def push_context(self):
        # a trick to remember global variables
        context = {'__globals__':[]}
        self._contexts.append(context)

    def pop_context(self):
        if len(self._contexts) <= 1:
            # NB: cannot pop the global context
            raise EnvContextsEmpty(self)
        return self._contexts.pop()

    def _get_context(self, var):
        cur = self.get_current_context()
        if var in cur['__globals__']:
            return self.get_global_context()
        return cur

    def get_global_context(self):
        return self._contexts[0]

    def get_current_context(self):
        return self._contexts[-1]

    def get_visible_context(self):
        # determine the currently visible context variables
        ctx = {}
        for env in self._contexts:
            for key,val in env.items():
                if key[0] != "_":
                    ctx[key] = val
        return ctx

    def add_global(self, name):
        gls = self.get_current_context()['__globals__']
        if not name in gls:
            gls.append(name)

    def get_description(self):
        env = self.get_visible_context()
        return "ENV :%d:\n%s\n%s\n%s" % (self.ip, "-" * 10,
            "\n".join(["%s: %s" % (key, env[key]) for key in sorted(env.keys())]),
            "-" * 10)
