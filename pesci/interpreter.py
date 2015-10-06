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

import sys
import traceback
import types
import ast
import operator
import pesci.code
import readline                 # enables line editing features
from pesci.errors import *
from pesci import ExecutionEnvironment, PesciCode

"""
Implements a python Abstract Syntax interpreter, which runs into a confined
environnment and understands only a subset of original python syntax.

The interpreter has the ability to step into single instructions into code,
easily achieved using the "yield" python command. Yield command mantains
the current call stack wherease a data stack is retained by
the ExecutionEnvironment push/pop functions.

The recurrent code snippet:

itr = self._fold_expr(env, node)
while itr:
    try: yield next(itr)
    except StopIteration: break
var = env.pop()

is used to "wait" until sub-folded functions end their execution.
"""

# builtin functions
BUILTINS = {'len':len, 'abs':abs, 'all':all, 'any':any, 'bin':bin, 'bool':bool,
 'cmp':cmp, 'complex':complex, 'dict':dict, 'enumerate':enumerate, 'filter':filter,
 'float':float, 'format':format, 'hasattr':hasattr, 'hash':hash, 'hex':hex, 'int':int,
 'list':list, 'long':long, 'map':map, 'max':max, 'min':min, 'oct':oct, 'ord':ord,
 'pow':pow, 'range':range, 'xrange':xrange, 'reduce':reduce, 'reversed':reversed,
 'round':round, 'slice':slice, 'sorted':sorted, 'str':str, 'sum':sum, 'type':type,
 'tuple':tuple, 'zip':zip}

# builtin types
BUILT_TYPES = {'None':None}

class Interpreter(object):
    def __init__(self):
        self._interactive = False

    """Creates a new virtual execution environment """
    def create_env(self, code=None):
        env = ExecutionEnvironment()
        if code:
            env.setup(code.get_ast(), BUILTINS, BUILT_TYPES)
        return env


    def _step_iterator(self, env):
        for node in ast.iter_child_nodes(env.code):
            itr = self._fold_expr(env, node)
            while itr:
                try: yield next(itr)
                except StopIteration: break
            try:
                # a zombie value
                val = env.pop()
                if self._interactive:
                    self.i_print(val)
            except IndexError:
                pass

    """Executes one step into the code, updating given environment.
       Returns current executing ast node or raises EnvExecEnd if execution
       is finished.
    """
    def step(self, env):
        if not env.iterator:
            env.iterator = self._step_iterator(env)
        try:
            node = next(env.iterator)
            env.ip += 1
            return node
        except StopIteration:
            raise EnvExecEnd(env)

    """Executes code until end"""
    def run(self, env, debug=False):
        while True:
            try:
                node = self.step(env)
                if debug:
                    print node
            except EnvExecEnd:
                break

    """Launch interactive mode"""
    def run_interactive(self, env):
        print "Pesci 0.1 over Python %s" % sys.version.split(" ")[0]
        print "Emanuele Faranda <black.silver@hotmail.it>"
        print "Type 'exit' to end interactive mode\n"
        notexit = True
        self._interactive = True
        partial = ""

        while notexit:
            try:
                if partial:
                    prompt = "... "
                else:
                    prompt = ">>> "
                cmd = raw_input(prompt)
            except EOFError:
                notexit = False
            except KeyboardInterrupt as kint:
                print "KeyboardInterrupt"
                partial = ""
            else:
                # handle continuation lines
                s = cmd.strip()
                if s and s[-1] == ":":
                    partial += cmd + "\n"
                elif partial:
                    if not cmd:
                        # end of command
                        cmd = partial
                        partial = ""
                    else:
                        partial += cmd + "\n"

                if cmd == "exit":
                    notexit = False
                elif not partial:
                    # evaluate command
                    try:
                        code = PesciCode.from_string(cmd)
                        env.setup(code.get_ast(), BUILTINS, BUILT_TYPES)
                        self.run(env)
                    except Exception as e:
                        traceback.print_exc(file=sys.stdout)
        self._interactive = False

    """Respond to a print instruction"""
    def i_print(self, s):
        print s

    def _fold_expr(self, env, node):
        # fold ones, may return iterators
        if isinstance(node, ast.BinOp):
            return self._statement_binop(env, node)
        elif isinstance(node, ast.BoolOp):
            return self._statement_boolop(env, node)
        elif isinstance(node, ast.UnaryOp):
            return self._statement_unaryop(env, node)
        elif isinstance(node, ast.Compare):
            return self._statement_compare(env, node)
        elif isinstance(node, ast.Assign):
            return self._statement_assign(env, node)
        elif isinstance(node, ast.AugAssign):
            return self._statement_augassign(env, node)
        elif isinstance(node, ast.Print):
            return self._statement_print(env, node)
        elif isinstance(node, ast.If):
            return self._statement_if(env, node)
        elif isinstance(node, ast.Expr):
            return self._statement_expr(env, node)
        elif isinstance(node, ast.FunctionDef):
            return self._statement_funcdef(env, node)
        elif isinstance(node, ast.Call):
            return self._statement_funcall(env, node)
        elif isinstance(node, ast.Return):
            return self._statement_return(env, node)
        elif isinstance(node, ast.Dict):
            return self._statement_dict(env, node)
        elif isinstance(node, ast.Tuple):
            return self._statement_tuple(env, node)
        elif isinstance(node, ast.List):
            return self._statement_list(env, node)
        elif isinstance(node, ast.Attribute):
            return self._statement_attribute(env, node)
        elif isinstance(node, ast.Global):
            return self._statement_global(env, node)
        else:
            # try with a base value
            v = self._base_value(env, node)
            env.push(v)

    def _base_value(self, env, node):
        if isinstance(node, (int, long, float, str, bool, list, tuple)) or node is None:
            return node
        elif isinstance(node, ast.Num):
            return node.n
        elif isinstance(node, ast.Str):
            return node.s
        elif isinstance(node, ast.operator):
            return node
        elif isinstance(node, ast.Name):
            return env.get_symbol(node.id)
        elif isinstance(node, ast.Pass):
            pass
        else:
            # TODO blablabla
            assert 0, "UNKNOWN! %s" % (node)

    def _perform_bin_op(self, left, op, right):
        ops = (ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Mod, ast.Pow, ast.LShift, ast.RShift, ast.BitOr, ast.BitXor, ast.BitAnd, ast.FloorDiv)
        mops = (operator.add, operator.sub, operator.mul, operator.div, operator.mod, operator.pow, operator.lshift, operator.rshift, operator.or_, operator.xor, operator.and_, operator.floordiv)

        for i in range(len(ops)):
            if isinstance(op, ops[i]):
                return mops[i](left, right)
        # TODO blablabla
        assert 0, "UNKNOWN BIN OP! %s" % (op)

    def _perform_bool_op(self, op, values):
        operator_logical_or = lambda a,b: a or b
        operator_logical_and = lambda a,b: a and b

        if isinstance(op, ast.Or):
            return operator.truth(reduce(operator_logical_or, values, 0))
        if isinstance(op, ast.And):
            return operator.truth(reduce(operator_logical_and, values, 1))
        else:
            # TODO blablabla
            assert 0, "UNKNOWN BOOL OP! %s" % (op)

    def _perform_unary(self, op, operand):
        if isinstance(op, ast.Not):
            return not operand
        elif isinstance(op, ast.Invert):
            # negazione logica
            return ~operand
        #TODO  UAdd | USub
        else:
            # TODO blablabla
            assert 0, "UNKNOWN UNARY OP! %s" % (op)

    def _perform_comparison(self, a, comp, b):
        operator_in = lambda x,l: x in l
        operator_not_in = lambda x,l: not (x in l)

        ops = (ast.Eq, ast.NotEq, ast.Lt, ast.LtE, ast.Gt, ast.GtE, ast.Is, ast.IsNot, ast.In, ast.NotIn)
        mops = (operator.eq, operator.ne, operator.lt, operator.le, operator.gt, operator.ge, operator.is_, operator.is_not, operator_in, operator_not_in)

        for i in range(len(ops)):
            if isinstance(comp, ops[i]):
                return mops[i](a, b)
        assert 0, "BAD COMPARISON %s" % comp

    def _statement_expr(self, env, node):
        itr = self._fold_expr(env, node.value)
        while itr:
            try: yield next(itr)
            except StopIteration: break
        # expr is now on the stack, if any

    def _statement_assign(self, env, node):
        itr = self._fold_expr(env, node.value)
        while itr:
            try: yield next(itr)
            except StopIteration: break

        val = env.pop()
        # TODO what else is supposed to hold??
        assert len(node.targets) == 1
        target = node.targets[0]

        # fold the lists
        if isinstance(val, list):
            l = []
            for v in val:
                itr = self._fold_expr(env, v)
                while itr:
                    try: yield next(itr)
                    except StopIteration: break
                l.append(env.pop())
            val = l

        # assign to a list of variables
        if (isinstance(target, ast.List) or isinstance(target, ast.Tuple)) and isinstance(val, list):
            i = 0
            for var in ast.iter_child_nodes(target):
                if isinstance(var, ast.Name):
                    env.setvar(var.id, val[i])
                    i += 1
        else:
            env.setvar(target.id, val)
        yield node

    def _statement_augassign(self, env, node):
        itr = self._fold_expr(env, node.value)
        while itr:
            try: yield next(itr)
            except StopIteration: break

        val = env.pop()
        newval = self._perform_bin_op(env.getvar(node.target.id), node.op, val)
        env.setvar(node.target.id, newval)
        yield node

    def _statement_binop(self, env, node):
        itr = self._fold_expr(env, node.left)
        while itr:
            try: yield next(itr)
            except StopIteration: break

        l = env.pop()
        itr = self._fold_expr(env, node.op)
        while itr:
            try: yield next(itr)
            except StopIteration: break

        op = env.pop()
        itr = self._fold_expr(env, node.right)
        while itr:
            try: yield next(itr)
            except StopIteration: break

        r = env.pop()
        env.push(self._perform_bin_op(l, op, r))
        yield node

    def _statement_boolop(self, env, node):
        op = node.op
        args = []
        for val in node.values:
            itr = self._fold_expr(env, val)
            while itr:
                try: yield next(itr)
                except StopIteration: break

            args.append(env.pop())

        env.push(self._perform_bool_op(op, args))
        yield node

    def _statement_unaryop(self, env, node):
        op = node.op
        itr = self._fold_expr(env, node.operand)
        while itr:
            try: yield next(itr)
            except StopIteration: break

        operand = env.pop()
        env.push(self._perform_unary(op, operand))
        yield node

    def _statement_compare(self, env, node):
        # need sequences for compare to distinguish between
        # x < 4 < 3 and (x < 4) < 3
        comparators = []
        for comp in node.comparators:
            itr = self._fold_expr(env, comp)
            while itr:
                try: yield next(itr)
                except StopIteration: break

            comparators.append(env.pop())
        comparators.insert(0, env.getvar(node.left.id))

        # let's say it's just one op -> 1 yield
        env.push(operator.truth(reduce(operator.and_,
            [self._perform_comparison(comparators[i],
                node.ops[i],
                comparators[i+1]) for i in range(len(node.ops))],
            1)))
        yield node

    def _statement_print(self, env, node):
        # NB: IGNORE node.dest, node.nl
        v = []
        needsspace = False
        for val in node.values:
            itr = self._fold_expr(env, val)
            while itr:
                try: yield next(itr)
                except StopIteration: break

            s = env.pop()
            if needsspace:
                v.append(" ")
            else:
                needsspace = True
            if isinstance(s, str) and len(s) and s[-1] == "\n":
                needsspace = False
            else:
                s = str(s)
            v.append(s)
        self.i_print("".join(v))
        yield node

    def _statement_if(self, env, node):
        itr = self._fold_expr(env, node.test)
        while itr:
            try: yield next(itr)
            except StopIteration: break

        cond = env.pop()
        if cond:
            to = node.body
        else:
            to = node.orelse
        for i in to:
            itr = self._fold_expr(env, i)
            while itr:
                try: yield next(itr)
                except StopIteration: break
        yield node

    def _statement_funcdef(self, env, node):
        # parse the arguments structure
        args = [arg.id for arg in node.args.args if isinstance (arg, ast.Name)]

        # NB: default n values are mapped to the last n arguments
        default = [self._base_value(env, defaul) for defaul in node.args.defaults]
        all_args = {'args':tuple(args), 'vararg':node.args.vararg, 'kwarg':node.args.kwarg, 'defaults':default}
        f = pesci.code.PesciFunction(node.name, all_args, node.body)
        env.setfunc(f.name, f)
        yield node

    def _statement_funcall(self, env, node):
        # get the args
        args = []
        for arg in node.args:
            itr = self._fold_expr(env, arg)
            while itr:
                try: yield next(itr)
                except StopIteration: break
            args.append(env.pop())
        args = {"args":args, "kwargs":node.keywords, "star":node.starargs, "kstar":node.kwargs}

        # get the kargs
        kwargs = {}
        for key in args['kwargs']:
            k = key.arg
            v = self._base_value(env, key.value)
            kwargs[k] = v

        # get the stars
        kstar = star = None
        if args['star']:
            star = env.getvar(args['star'].id)
        if args['kstar']:
            kstar = env.getvar(args['kstar'].id)

        # append star and kstar to the values
        allargs = list(args['args'])
        if star:
            for val in star:
                allargs.append(val)
        if kstar:
            for key,val in kstar.items():
                kwargs[key] = val

        # get the function
        if isinstance(node.func, ast.Name):
            try:
                f = env.getfunc(node.func.id)
            except EnvFuncNotFound as e:
                try:
                    f = env.get_builtin(node.func.id)
                except KeyError:
                    raise e
        else:
            itr = self._fold_expr(env, node.func)
            while itr:
                try: yield next(itr)
                except StopIteration: break
            f = env.pop()

        # handle builtins
        if isinstance(f, types.BuiltinFunctionType):
            env.push(f(*allargs, **kwargs))
            yield
            return

        # enter the function context
        env.push_context()
        toassign = list(f.args['args'])
        #~ print "call %s = %s(%s <= %s)" % (f, node.func.id, f.args, args)

        # bind default values
        defaults = f.args['defaults']
        argnames = f.args['args']
        wasdef = []
        k = len(argnames) - len(defaults)
        for d in defaults:
            env.setvar(argnames[k], d)
            wasdef.append(argnames[k])
            toassign.remove(argnames[k])
            k += 1

        # bind positional values
        k = 0
        for arg in allargs:
            try:
                argname = argnames[k]
            except IndexError:
                break

            env.setvar(argname, arg)
            try:
                toassign.remove(argname)
            except ValueError:
                pass
            k += 1
        remargs = allargs[k:]

        # bind keyword values
        skwargs = {}
        for k,v in kwargs.items():
            if k in argnames:
                if not k in toassign and not k in wasdef:
                    # double assignment
                    raise BadFunctionCall(f)
            elif f.args['kwarg']:
                skwargs[k] = v
            else:
                raise BadFunctionCall(f)

            env.setvar(k, v)
            try:
                toassign.remove(k)
            except ValueError:
                pass

        # expose remaining kwarg and vararg
        if f.args['vararg']:
            env.setvar(f.args['vararg'], remargs)
        if f.args['kwarg']:
            env.setvar(f.args['kwarg'], skwargs)

        if toassign:
            raise BadFunctionCall(f)

        # we are ready to jump!
        for istr in f.body:
            itr = self._fold_expr(env, istr)
            while itr:
                try: yield next(itr)
                except StopIteration: break

        env.pop_context()
        yield node

    def _statement_return(self, env, node):
        itr = self._fold_expr(env, node.value)
        while itr:
            try: yield next(itr)
            except StopIteration: break

        # just to be explicit
        env.push(env.pop())
        yield node

    def _statement_dict(self, env, node):
        # get the values
        values = []
        for val in node.values:
            itr = self._fold_expr(env, val)
            while itr:
                try: yield next(itr)
                except StopIteration: break
            values.append(env.pop())

        # get the keys
        keys = []
        for val in node.keys:
            itr = self._fold_expr(env, val)
            while itr:
                try: yield next(itr)
                except StopIteration: break
            keys.append(env.pop())

        # build the dict
        d = dict(zip(keys, values))
        env.push(d)
        yield node

    def _statement_tuple(self, env, node):
        l = []
        for val in node.elts:
            itr = self._fold_expr(env, val)
            while itr:
                try: yield next(itr)
                except StopIteration: break
            l.append(env.pop())
        env.push(tuple(l))
        yield node

    def _statement_list(self, env, node):
        l = []
        for val in node.elts:
            itr = self._fold_expr(env, val)
            while itr:
                try: yield next(itr)
                except StopIteration: break
            l.append(env.pop())
        env.push(l)
        yield node

    def _statement_attribute(self, env, node):
        itr = self._fold_expr(env, node.value)
        while itr:
            try: yield next(itr)
            except StopIteration: break
        item = env.pop()

        if node.attr[0] == "_":
            raise RuntimeError("invalid attribute '%s'" % node.attr)
        env.push(getattr(item, node.attr))
        yield node

    def _statement_global(self, env, node):
        for name in node.names:
            env.add_global(name)
        yield node
