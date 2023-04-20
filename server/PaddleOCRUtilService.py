from paddleocr import PaddleOCR
import asyncio
import time
from . import utils
from . import objectPool
from .config import ThreadPool,logger

rec_model_dir = ""
cls_model_dir= ""
det = "..\\ocr_model\\ch_ppocr_server_v2.0_det_infer"
rec = "..\\ocr_model\\\ch_ppocr_mobile_v2.0_rec_infer"

def create_new_object() ->PaddleOCR:
    return PaddleOCR(use_angle_cls=True, lang="ch",page_num=1,det=det,rec=rec,use_tensorrt=True,enable_mkldnn=True)

_objectSize = 4
paddleOcrPoll = objectPool.ObjectPool(create_new_object,_objectSize)

loop = asyncio.get_event_loop()

class PaddleOCRUtil(metaclass=utils.Singleton):
    
    # @utils.calc_self_time
    def image_ocr(self,img_path) -> list:
        data: list = list()
        logger.debug(f"开始解析{img_path}")
        logger.debug(f"对象池{paddleOcrPoll.size()}")
        # lock.acquire()
        ocr = paddleOcrPoll.acquire()
        try:
            result = ocr.ocr(img_path, cls=True)
            for idx in range(len(result)):
                res = result[idx]
                for line in res:
                    data.append(line)
        finally:
            # lock.release()
            paddleOcrPoll.release(ocr)
            logger.debug(f"解析{img_path}完成")
        return img_path,data


    # @utils.calc_self_time
    async def parserImage(self,files) -> dict:
        loop = asyncio.get_running_loop()
        tasks = [loop.run_in_executor(ThreadPool, self.image_ocr, file) for file in files]
        image_data = await asyncio.gather(*tasks)
        results = {}
        for image in image_data:
            strs = []
            filename, data = image
            for i in  data:
                strs.append(i[1][0])
            results[filename.split("\\")[-1]] = strs
        return results
        

class PaddleOCRService(metaclass=utils.Singleton):

    def __init__(self,paddleOCRUtil:PaddleOCRUtil) -> None:
        self.paddleOCRUtil =  paddleOCRUtil
    
    async def __process_files(self, files):
        result = await self.paddleOCRUtil.parserImage(files=files)
        return result
       
    def parserImage_run(self, files) -> dict:
        loop = asyncio.new_event_loop()
        tasks = [loop.create_task(self.__process_files(files=i)) for i in utils.split_array(files, 8)]
        wait_coro = asyncio.wait(tasks)
        loop.run_until_complete(wait_coro)
        data = {}
        for i in range(len(tasks)):
            data.update(tasks[i].result())
        return data
