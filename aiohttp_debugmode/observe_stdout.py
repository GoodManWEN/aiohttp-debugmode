import asyncio

async def spying(porc):
    while True:
        rev = await porc.async_readline()
        if rev == None:
            break
        if rev != '\n':
            print(rev,end='')


async def flusher(logger):
    for x in range(100):
        await asyncio.sleep(0.01)
        logger.debug('')
    while True:
        await asyncio.sleep(0.2)
        logger.debug('')