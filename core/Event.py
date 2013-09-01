# -*- coding: utf-8 -*-
"""
Created on Sun Sep  1 14:26:12 2013

"""


class Event:
    """Event support class"""
    def __init__(self):
        self.handlers = set()

    def handle(self, handler):
        self.handlers.add(handler)
        return self

    def unhandle(self, handler):
        try:
            self.handlers.remove(handler)
        except:
            raise ValueError("Handler is not handling this event, "
                                    "so cannot unhandle it.")
        return self

    def fire(self, *args, **kargs):
        for handler in self.handlers:
            handler(*args, **kargs)

    def getHandlerCount(self):
        return len(self.handlers)

    __iadd__ = handle
    __isub__ = unhandle
    __call__ = fire
    __len__ = getHandlerCount


if(__name__ == '__main__'):
    def receiver_func(message):
        print("receiver_func " + str(message))

    class EventExampleSender:
        def __init__(self):
            self.event = Event()

        def raise_event(self, message):
            self.event(message)

    class EventExampleReceiver:
        def __init__(self, id):
            self.event = Event()
            self.id = id

        def event_received(self, message):
            print("Received... " + self.id + " " + str(message))

    sender = EventExampleSender()
    receiver1 = EventExampleReceiver("1")
    receiver2 = EventExampleReceiver("2")

    sender.event += receiver1.event_received
    sender.event += receiver2.event_received
    sender.event += receiver_func

    sender.raise_event("Hi there")
    sender.raise_event(88)
