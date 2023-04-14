import asyncio


class async_task:

    def __init__(self,func) -> None:
        self.func = func
        self.task = None 

    async def run_async(self):
        self.task =  self.func()
        return self.task

    async def __await(self):
        return await self.task

    async def list_async(self, lis:list):
        async for i in lis:
            yield i



# class asyncioUtil:
#     loop = asyncio.get_event_loop()

#     def run_tasks(self,  ):
#         task = [result(url) for url in url_list]
       
#         loop.run_until_complete(asyncio.wait(task))

    