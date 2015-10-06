# python-pesci
Python environments & simple code interpreter

Pesci is a python 2 module which provides controlled execution of a subset of
python code, called PesciCode, into light virtual environments.

The PesciCode
-------------
The PesciCode aims to be a simple imperative language with a clean and
powerful syntax. The python language has been used as a base to create such
a language. Thanks to the python [Abstract Syntax Tree](https://docs.python.org/2/library/ast.html) module, the definition
of the functionalities of the language is just a matter of choosing the
wanted node types from the AST exposed ones and linking them up with some
semantics to create an interpreter.

Supported (scripting):
  - Strings, Lists, Tuples, Dicts
  - Fuction definitions and calls
  - Some builtin functions
  - Objects attribute access and methods calls
  
Not supported:
  - Class definitions
  - Function decorators
  - Files
  - Exceptions
  - Imports
  - Thread stuff
  - With statements
  - ...
  
Planned support:
  - If, While, For loops

The virtual environments
------------------------
The PesciCode interpreter definition is based on the concept of Environment.
An Environment is a standalone python namespace which is implemented with
a simple dict object. Variables and function definitions are wrapped into
python types and pushed into the environment. Thanks to this separation, it
is possible to run PesciCode into a confined environment, denying access to
python system modules and bultins. Moreover, access to "underscore" names
is denied. It is also possible to inject own objects and functions during
the environment setup phase.

In this way, you can wrap your objects into a python interface, load it into
a controlled python environment, and allow the user to use PesceCode as a
scripting language without allowing direct execution of python code...worderfull!

The single step execution
-------------------------
Pesci interpreter uses heavily python generators to provide single step
execution of python statements. The data stack of the operation is backed to
a list, whereas the code stack is implicitly wrapped into python generators.
This is transparent to the interface; just call interpreter.step() to cast
the magic and get a ast.node which is the descriptor of the executed step.

Interactive mode
----------------
Code can be either loaded from file or run in interactive mode. When the
interpreter is invoked with argument, the first mode is activated. When no
argument is provided, interactive mode is entered.
In order to invoke the interpreter, run the command `python pesci`.
