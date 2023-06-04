from . import config
from . import utils
from .asyncUtils import AsyncUtils
import os
import time
import asyncio


class PaddleOCRUtil(metaclass=utils.Singleton):

    @utils.calc_self_time
    def image_ocr(self, img_path) -> tuple:
        data: list = list()
        # lock.acquire()
        time.sleep(0.5)
        return img_path, data
    
    @utils.calc_self_time
    async def __image_ocr(self, files) -> tuple:
        for i in files:
            yield await self.image_ocr(i) 

    # @utils.calc_self_time
    async def parserImage(self, files) -> list:
        print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
        loop = asyncio.get_running_loop()
        tasks = [loop.run_in_executor(config.ThreadPool, self.__image_ocr, file) for file in utils.split_array(files, 10)]
        return tasks


class PaddleOCRService(metaclass=utils.Singleton):

    def __init__(self, paddleOCRUtil: PaddleOCRUtil) -> None:
        self.paddleOCRUtil = paddleOCRUtil

    async def parserImage_run(self, files) -> dict:
        loop = asyncio.get_event_loop()
        tasks = [loop.create_task(self.paddleOCRUtil.parserImage(files=i)) for i in utils.split_array(files, 10)]
        # tasks = [loop.create_task(self.paddleOCRUtil.parserImage(files))]
        results = {}
        for task in await asyncio.gather(*tasks):
            strs = []
            for image_ocr in  task:
                filename, data = await image_ocr
                for i in data:
                    strs.append(i[1][0])
                    results[filename.split("\\")[-1]] = strs
        return results


@utils.calc_time
def ocr_test():
    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    files = [f"/wdawda_{i}"  for i in range(100)]
    data = AsyncUtils.run(PaddleOCRService(
        PaddleOCRUtil()).parserImage_run(files))
    try:
        remove = list(map(lambda x: os.remove(x), files))
        AsyncUtils.to_thread(remove)
        files = None
    except OSError as e:
        print(f"Error deleting file: {e}")
    return data
