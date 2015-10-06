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
        self._builtins = {}

        # create global context
        self.push_context()

    def setup(self, code, builtins={}, builtvars={}):
        self.code = code
        self.ip = 0
        self.iterator = None
        self._builtins = builtins
        self._builtvars = builtvars

    def getvar(self, vid):
        try:
            var = self._get_from_contexts(vid)
        except KeyError:
            raise EnvVarNotFound(self, vid)
        return var

    """any symbol, function, name, ..."""
    def get_symbol(self, sid):
        try: return self.getvar(sid)
        except EnvVarNotFound:
            try: return self.getfunc(sid)
            except EnvFuncNotFound:
                try: return self.get_builtin(sid)
                except KeyError:
                    raise EnvSymbolNotFound(self, sid)

    def _set_in_context(self, context, key, val):
        context[key] = val

    def _get_from_contexts(self, key):
        # search a key in the context stack
        for context in reversed(self._contexts):
            if context.has_key(key):
                return context[key]
        # search in builtvars
        if key in self._builtvars:
            return self._builtvars[key]
        raise KeyError(key)

    def setvar(self, vid, val):
        if vid and vid[0] == "_":
            raise EnvBadSymbolName(self, vid)
        self._set_in_context(self._get_context(vid), vid, val)

    def setfunc(self, fid, fdef):
        if fid and fid[0] == "_":
            raise EnvBadSymbolName(self, fid)
        self._set_in_context(self._get_context(fid), fid, fdef)

    def getfunc(self, fid):
        try:
            f = self._get_from_contexts(fid)
        except KeyError:
            raise EnvFuncNotFound(self, fid)
        if not isinstance(f, pesci.code.PesciFunction):
            raise EnvFuncNotFound(self, fid)
        return f

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

    def set_builtins(self, d):
        self._builtins = d

    def get_builtin(self, f):
        return self._builtins[f]

    def add_global(self, name):
        gls = self.get_current_context()['__globals__']
        if not name in gls:
            gls.append(name)

    def get_description(self):
        env = self.get_visible_context()
        return "ENV :%d:\n%s\n%s\n%s" % (self.ip, "-" * 10,
            "\n".join(["%s: %s" % (key, env[key]) for key in sorted(env.keys())]),
            "-" * 10)
