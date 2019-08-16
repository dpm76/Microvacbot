import asyncio

async def sleep(delay):
    asyncio.sleep(delay)
    
async def sleep_ms(delay):
    asyncio.sleep(delay/1e3)
    
def get_event_loop():
    asyncio.get_event_loop()