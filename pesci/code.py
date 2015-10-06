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
import re
from pesci.errors import *
from pesci import Validator

# Used to denote our builtin functions, expecting interpreter + environment args
PESCI_BUILTIN_FUNCTION = "__pesci_builtinfun"
# The actual decorator to use
def pesci_function(func):
    setattr(func, PESCI_BUILTIN_FUNCTION, True)
    return func

class PesciFunction:
    def __init__(self, name, params, body):
        self.name = name
        self.args = params
        self.body = body

class PesciCode:
    def __init__(self, lines, validator):
        self._lines = lines
        self._code = "\n".join(self._lines)
        self._validator = validator
        self._ast_tree = None

    """
    Interpret source file and build a Code object.
    """
    @staticmethod
    def from_file(f):
        if not isinstance(f, file):
            f = file(f)
        # Remove \n
        lines = [line[:-1] for line in f]
        return PesciCode(lines, Validator())

    @staticmethod
    def from_string(s):
        lines = PesciCode._escape_newlines(s).split("\n")
        return PesciCode(lines, Validator())

    """replace \n within quotes with escaped version"""
    @staticmethod
    def _escape_newlines(code):
        replaces = [(m.start(0), m.end(0)) for m in re.finditer(r"['\"](.*?\n*?)['\"]", code) if "\n" in m.group(0)]
        i = 0
        parts = []
        for start,end in replaces:
            k = 0
            while k != -1:
                k = code.find("\n", start, end)
                if k != -1:
                    parts.append(code[i:k])
                    i = k+1
                    start = i
        parts.append(code[i:])
        return "\\n".join(parts)

    """Generate ast.tree from own code"""
    def _compile(self):
        try:
            # mode 'exec' tells we are compiling multiple statements
            parsed = ast.parse(self._code, mode='exec')
            self._validator.validate(parsed)
            return parsed
        except SyntaxError as error:
            # TODO exc handle
            raise
            #~ print "Error:", error
            #~ return None

    def __str__(self):
        return "PesciCode:%d chars\n%s\n%s\n%s" % (len(self._code),
            "*" * 10,
            "\n".join(
                map(lambda (n,s): "%03d| %s" % (n, s),
                    # add line numbers and print code
                    enumerate(self._lines) ),
                ), "*" * 10)

    def get_ast(self):
        # lazy
        if not self._ast_tree:
            self._ast_tree = self._compile()
        return self._ast_tree

    def _visit_ast_tree(self, rootnode, line=0, offset=0, indent=0):
        for node in ast.iter_child_nodes(rootnode):
            # Update line information
            if hasattr(node, "lineno"):
                line = node.lineno
                offset = node.col_offset

            print "%s%s at %d:%d" % (" "*indent, node, line, offset)
            self._visit_ast_tree(node, line, offset, indent+4)

    def print_ast(self):
        self._visit_ast_tree(self.get_ast())
