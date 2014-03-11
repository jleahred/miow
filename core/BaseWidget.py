# -*- coding: utf-8 -*-
"""
Created on Sun Dec  8 22:27:50 2013

@author: maiquel
"""

class BaseWidget(object):
    def bw_add_command_list(self, command_list):
        pass

    def bw_lock_command_window(self):
        False

    def __init__(self, *args):
        #super(BaseWidget, self).__init__()
        pass
    
    # property file_name
    # close_requested
    # save