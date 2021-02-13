'''
Created on 13 feb. 2021

@author: David
'''
from micropython import const
from uasyncio import StreamReader
from io import IOBase


MP_STREAM_POLL_RD = const(1)
MP_STREAM_POLL = const(3)
MP_STREAM_ERROR = const(-1)

class IrqEvent(IOBase):
    '''
    Event class to be used within IRQ handlers, since uasyncio's Event doesn't work properly.
    Taken from https://github.com/peterhinch/micropython-async/blob/master/v3/primitives/tests/irq_event_test.py 
    '''
    
    def __init__(self):
        self.state = False  # False=unset; True=set
        self.sreader = StreamReader(self)

    async def wait(self):
        await self.sreader.read(1)
        self.state = False

    def set(self):
        self.state = True

    def is_set(self):
        return self.state

    def read(self, _):
        pass

    def clear(self):
        pass  # See docs

    def ioctl(self, req, arg):
        ret = MP_STREAM_ERROR
        if req == MP_STREAM_POLL:
            ret = 0
            if arg & MP_STREAM_POLL_RD:
                if self.state:
                    ret |= MP_STREAM_POLL_RD
        return ret
