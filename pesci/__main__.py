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
from pesci import *

@pesci_function
def pesci_help(**kargs):
    interpreter = kargs[PESCI_KEY_INTERPRETER]
    env = kargs[PESCI_KEY_ENV]

    interpreter.print_line("No help available. Try with 'dir()'.")

@pesci_function
def pesci_dir(**kargs):
    interpreter = kargs[PESCI_KEY_INTERPRETER]
    env = kargs[PESCI_KEY_ENV]
    interpreter.print_line(env.get_description())

preloaded_symbols = {
    'help' : pesci_help,
    'dir' : pesci_dir
}

if __name__ == "__main__":
    if len(sys.argv) > 2:
        print "Usage: %s [+][source file]" % sys.argv[0]
        print "NB: the plus sign enables debug mode"
        exit(1)

    interpreter = Interpreter()
    if len(sys.argv) == 1:
        # run in interactive mode
        env = interpreter.create_env(symbols=preloaded_symbols)
        interpreter.run_interactive(env)
    else:
        # run from file
        if sys.argv[1].startswith("+"):
            fname = sys.argv[1].lstrip("+")
            debug = True
        else:
            fname = sys.argv[1]
            debug = False
        code = PesciCode.from_file(fname)
        env = interpreter.create_env(code)

        if debug:
            # print code info
            print "\n", code
            code.print_ast()
            print "\n", "*" * 20

        interpreter.run(env, debug=False)

        if debug:
            # also run in python interpreter to compare
            print "\n", env.get_description()
            print "\nREAL:\n", "*" * 20
            eval(compile(code.get_ast(), "<string>", mode="exec"))
            print "----------"
            for var in sorted(env.get_visible_context().keys()):
                print "%s:" % var, globals()[var]
            print "----------"
            print "*" * 20

            # Enter the interactive mode
            interpreter.run_interactive(env)
