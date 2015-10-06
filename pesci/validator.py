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
from pesci.errors import *

# Recognised subset of python
PESCI_SUBSET = (
    #-- Algebraic, Bitwise, Compare, Unary, Boolean operators
    ast.operator, ast.cmpop, ast.unaryop, ast.UnaryOp, ast.boolop, ast.BoolOp, ast.BinOp,

    #-- Control flow
    ast.For, ast.While, ast.If,

    #-- Function and Class stuff
    ast.keyword, ast.arguments, ast.Return, ast.Assign, ast.Expr,
    ast.AugAssign, ast.FunctionDef, ast.IfExp,

    #-- Tuple Dict stuff - Tuple: only for assignment
    ast.slice, ast.Dict, ast.Tuple, ast.List, ast.ListComp, ast.DictComp, ast.Call,

    #-- Expression stuff
    ast.Load, ast.AugLoad, ast.AugStore, ast.Store, ast.Param, ast.Name,

    #-- Other stuff
    ast.Print, ast.Global, ast.Pass, ast.Break, ast.Continue, ast.Num,
    ast.Str, ast.Compare, ast.Attribute
)

class Validator(object):
    """Only recognize a subset of python commands"""
    def _is_valid_node(self, node):
        if [op for op in PESCI_SUBSET if isinstance(node, op)]:
            return True
        return False

    """Recursively visits parsed tree"""
    def _visit_ast_tree(self, rootnode, line=0, offset=0, level=0):
        for node in ast.iter_child_nodes(rootnode):
            # Update line information
            if hasattr(node, "lineno"):
                line = node.lineno
                offset = node.col_offset

            if not self._is_valid_node(node):
                raise PesciSyntaxError(node, line, offset)

            self._visit_ast_tree(node, line, offset, level+1)

    def validate(self, ast_tree):
        # validate using python ast module
        self._visit_ast_tree(ast_tree)
        #~ code = compile(ast_tree, '<string>', 'exec')
