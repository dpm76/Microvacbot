'''
Created on 22 de may. de 2016

@author: david
'''

class EventHook(object):
    '''
    Event Pattern from: http://www.voidspace.org.uk/python/weblog/arch_d7_2007_02_03.shtml#e616
    '''

    def __init__(self):
        self._handlers = []

    def __iadd__(self, handler):
        self._handlers.append(handler)
        return self

    def __isub__(self, handler):
        self._handlers.remove(handler)
        return self

    def fire(self, *args, **keywargs):
        for handler in self._handlers:
            handler(*args, **keywargs)

    def clearObjectHandlers(self, inObject):
        for theHandler in self._handlers:
            if theHandler.im_self == inObject:
                self -= theHandler
                
