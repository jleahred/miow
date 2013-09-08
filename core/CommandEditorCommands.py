# -*- coding: utf-8 -*-
"""
Created on Sun Sep  8 14:28:40 2013
@author: maiquel

try h(), or h(core.Commands) or even h(h)


"""


import inspect


if(__name__ == '__main__'):
    import os
    import sys
    lib_path = os.path.abspath('..')
    sys.path.append(lib_path)

import core.CommandEditorCommands


def h(thing=None):
    """\
h is a function to get information about an element

I will print on console the information about the provided parameter
This parameter can be a module, a class, a method or a function

* Modules: doc, classes and functions
* Classes: doc, methods, and members
* Methods: doc
* Functions: doc

NOTE: To get information with h() you have to import the module previously
"""

    def get_data_same_module(thing):
        for name, data in inspect.getmembers(thing):
            if inspect.ismodule(inspect.getmodule(data)):
                current_module = inspect.getmodule(data)
                if current_module.__name__ == inspect.getmodule(
                                                        thing).__name__:
                    yield name, data

    def get_info_from_module(module):
        r_classes = []
        r_functs = []
        for name, data in get_data_same_module(module):
            if inspect.isclass(data):
                r_classes.append(name)
            elif inspect.isfunction(data):
                r_functs.append(name)
        return r_classes, r_functs, inspect.getdoc(module)

    def get_info_from_class(cls):
        r_methods = []
        r_properties = []
        for name, data in get_data_same_module(cls):
            if inspect.ismethod(data):
                r_methods.append(name)
        return r_methods, r_properties, inspect.getdoc(cls)

    if thing == None:
        #print(__doc__)
        print(h.__doc__)
        h(core.CommandEditorCommands)

    if inspect.ismodule(thing):
        classes, functions, doc = get_info_from_module(thing)
        print("MODULE: %s" % thing.__name__)

        print("\n%s\n\n" % doc)

        print("\nclasses:")
        for c in classes:
            print("    %s" % c)

        print("\nfunctions:")
        for c in functions:
            print("    %s" % c)

    elif inspect.isclass(thing):
        methods, properties, doc = get_info_from_class(thing)
        print("CLASS: %s" % thing.__name__)

        print("\n%s\n\n" % doc)

        print("\nmethods:")
        for c in methods:
            print("    %s" % c)

        print("\nproperties:")
        #for c in functions:
        #    print("    %s" % c)

    elif inspect.isfunction(thing):
        print("FUNCTION: %s" % thing.__name__)

        print("\n%s\n\n" % inspect.getdoc(thing))


def clear():
    """\
It will delete the result console"""
    pass


def reset():
    """\
It will restart the console deleting all in the current session"""
    pass


if(__name__ == '__main__'):
    import core.Commands
    import core.CommandEditor

    print("\n\n***************************************")
    h()
    print("\n\n***************************************")
    h(core.Commands)
