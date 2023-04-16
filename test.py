import asyncio

async def async_generator():
    for i in range(3):
        await asyncio.sleep(1)
        print(i,"start")
        yield i
        print(i,"end")

async def main():
    async for value in async_generator():
        print(value)
        print("next",value)

loop = asyncio.new_event_loop()
loop.run_until_complete(main())


loop1 = asyncio.get_event_loop()
loop1.run_until_complete(main())
