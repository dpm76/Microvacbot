import asyncio
from asyncio import Event, wait_for, run, create_task, Lock,StreamReader

async def sleep(delay):
    asyncio.sleep(delay)
    
async def sleep_ms(delay):
    asyncio.sleep(delay/1e3)
    
def get_event_loop():
    asyncio.get_event_loop()
    
Event=Event
wait_for=wait_for
run=run
create_task=create_task
Lock=Lock
StreamReader=StreamReader