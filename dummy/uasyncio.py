import asyncio

async def sleep(delay):
    asyncio.sleep(delay)
    
    
def get_event_loop():
    asyncio.get_event_loop()