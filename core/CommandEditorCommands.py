# -*- coding: utf-8 -*-
"""\
    Created on Sun Sep  8 14:28:40 2013
    @author: maiquel

    Here we have commands (python functions) that can be called directly from
    the interpreter
"""


import inspect


if(__name__ == '__main__'):
    import os
    import sys
    lib_path = os.path.abspath('..')
    sys.path.append(lib_path)

import core.CommandEditorCommands
import core.CommandEditor


from Event import Event

EVENT_COMMAND_CLEAR = Event()
EVENT_COMMAND_RESET = Event()


def h(thing="__empty__"):
    """\
    h is a function to get information about an element

    It's similar to python help function but reducing information to show

    I will print on console the information about the provided parameter
    This parameter can be a module, a class, a method or a function

        * Modules: doc, classes and functions
        * Classes: doc, methods, and members
        * Methods: doc
        * Functions: doc


    Interesting help commands
        h()
        h(cw)
        h(mw)
        h(app)


    NOTE: To get information with h(thing) you have to import the
    related module previously
"""

    def get_data_same_module(thing):
        for name, data in inspect.getmembers(thing):
            if inspect.ismodule(inspect.getmodule(data)):
                current_module = inspect.getmodule(data)
                if current_module.__name__ == inspect.getmodule(
                                                        thing).__name__:
                    yield name, data
            elif inspect.isdatadescriptor(data):
                yield name, data

    def get_info_from_module(module):
        r_classes = []
        r_functs = []
        for name, data in get_data_same_module(module):
            if inspect.isclass(data):
                r_classes.append(name)
            elif inspect.isfunction(data):
                r_functs.append(name)
        #return r_classes, r_functs, inspect.getdoc(module)
        return r_classes, r_functs, module.__doc__

    def get_info_from_class(cls):
        r_methods = []
        r_properties = []
        for name, data in get_data_same_module(cls):
            if inspect.ismethod(data):
                r_methods.append(name)
            elif inspect.isdatadescriptor(data):
                r_properties.append(name)
        #return r_methods, r_properties, inspect.getdoc(cls)
        return r_methods, r_properties, cls.__doc__

    if thing == "__empty__":
        #print(__doc__)
        print("\n\n\n\n" + core.CommandEditor.WELLCOME_MESSAGE)
        print(h.__doc__)
        h(core.CommandEditorCommands)
        #print("\n\nCURRENT_WIDGET..............................")
        #if core.CommandEditor.get_current_widget():
        #    h(core.CommandEditor.get_current_widget())
        #else:
        #    print("None")
        #print("\n\nMAIN_WINDOW..............................")
        #if core.CommandEditor.get_main_window():
        #    h(core.CommandEditor.get_main_window())
        #else:
        #    print("None")
        return

    if inspect.ismodule(thing):
        classes, functions, doc = get_info_from_module(thing)
        print("\nMODULE: %s" % thing.__name__)

        print("\n%s" % doc)

        if len(classes):
            print("\n    classes:")
            for c in classes:
                print("        %s" % c)

        if len(functions):
            print("\n    functions:")
            for c in functions:
                print("        %s" % c)

    elif inspect.isfunction(thing):
        print("\nFUNCTION: %s" % thing.__name__)
        print("    " + str(inspect.getargspec(thing)))
        print("\n%s" % inspect.getdoc(thing))

    elif inspect.ismethod(thing):
        print("\nMETHOD: %s" % thing.__name__)
        print("    " + str(inspect.getargspec(thing)))
        print("\n%s" % thing.__doc__)

    elif inspect.isclass(thing):
        methods, properties, doc = get_info_from_class(thing)
        print("\nCLASS: %s" % thing.__name__)

        print("\n%s" % doc)

        print("\n    properties:")
        for c in properties:
            print("        %s" % c)

        print("\n    methods:")
        for c in methods:
            print("        %s" % c)

    elif inspect.isclass(type(thing)):
        methods, properties, doc = get_info_from_class(type(thing))
        print("\nINSTANCE FROM: %s" % type(thing).__name__)

        print("\n%s" % doc)

        print("\n    properties:")
        for c in properties:
            print("        %s" % c)

        print("\n    methods:")
        for c in methods:
            print("        %s" % c)

        #print("\nproperties:")
        #for c in functions:
        #    print("    %s" % c)

    else:
        print("\n???: ")
        print("\n%s" % inspect.getdoc(thing))


def clear():
    """\
It will delete the result console"""
    EVENT_COMMAND_CLEAR()


def reset():
    """\
It will restart the console deleting all in the current session"""
    EVENT_COMMAND_RESET()


if(__name__ == '__main__'):
    print("\n\n***************************************")
    h()
    print("\n\n***************************************")
    h(core.CommandEditorCommands)
