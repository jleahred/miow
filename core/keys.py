# -*- coding: utf-8 -*-
"""
Created on Thu Oct 10 22:54:17 2013

@author: maiquel
"""


from  PyQt4.QtGui import(QKeyEvent)

from  PyQt4.QtCore import (Qt,
                           QEvent)


def get_key_event_from_dict(key_info):
    return QKeyEvent(QEvent.KeyPress,
        key_info["key"],
        Qt.KeyboardModifiers(key_info["modifiers"]),
        key_info["text"],
        key_info["autorepeat"],
        key_info["count"])


def get_dict_from_key_event(key_event):
    return {
        "key": key_event.key(),
        "modifiers": int(key_event.modifiers()),
        "text": key_event.text(),
        "autorepeat": key_event.isAutoRepeat(),
        "count": key_event.count()
    }


def get_key_event_from_dict_simpl(key_info):
    return QKeyEvent(QEvent.KeyPress,
        key_info["key"],
        Qt.KeyboardModifiers(key_info["modifiers"]),
        key_info["text"],
        False,
        1)


def get_dict_from_key_event_simpl(key_event):
    return {
        "key": key_event.key(),
        "modifiers": int(key_event.modifiers()),
        "text": key_event.text()
    }
