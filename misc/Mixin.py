# -*- coding: utf-8 -*-
"""
Mixin function to create a new class mixins
"""


def mixin(base, *mixs):
    """
    Mixin will return a type mixings the classes passed.
    Reverse order compared with Python mixins
    """
    def mixin__internal(base, addition):
        """Internal closure"""
        class NewClass(addition, base):
            """Created class mixings the params"""
            def __init__(self, *args):
                base.__init__(self, *args)
                addition.__init__(self, *args)
        return NewClass

    new_class = base
    for mix in mixs:
        new_class = mixin__internal(new_class, mix)
    return new_class


# TEST
if(__name__ == '__main__'):
    class WithAdd:
        """An example creating an extension with add method"""
        def __init__(self, *args):
            pass

        def add(self, value):
            """This is the method added by this class"""
            return self.number + value

    class WithSubs:
        """An example creating an extension with subs method"""
        def __init__(self, *args):
            pass

        def subtract(self, value):
            """This is the method added by this class"""
            return self.number - value

    class MyClass:
        """Just a base class to be extended in the example"""
        def __init__(self, number):
            self.number = number

    def test_2():
        """simple test mixing 2 by 2"""
        MixedClass_ = mixin(MyClass, WithAdd)
        MixedClass = mixin(MixedClass_, WithSubs)
        my_instance = MixedClass(4)
        print my_instance.add(2)
        print my_instance.subtract(2)

    def test_n():
        """simple test mixing 3 at once"""
        MixedClass = mixin(MyClass, WithAdd, WithSubs)
        my_instance = MixedClass(40)
        print my_instance.add(2)
        print my_instance.subtract(2)

    test_2()
    test_n()
