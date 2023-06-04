from paddleocr import PaddleOCR
import asyncio
import time
from . import utils
from . import objectPool
from .config import ThreadPool,log,objectPoolSize

rec_model_dir = ""
cls_model_dir= ""
det = "..\\ocr_model\\ch_ppocr_server_v2.0_det_infer"
rec = "..\\ocr_model\\\ch_ppocr_mobile_v2.0_rec_infer"

def create_new_object() ->PaddleOCR:
    return PaddleOCR(use_angle_cls=True, lang="ch",page_num=1,det=det,rec=rec,use_tensorrt=True,enable_mkldnn=True)

paddleOcrPoll = objectPool.ObjectPool(create_new_object,objectPoolSize)

loop = asyncio.get_event_loop()

class PaddleOCRUtil(metaclass=utils.Singleton):
    
    # @utils.calc_self_time
    async def image_ocr(self,img_path) -> list:
        log.debug(time.ctime(time.time()),img_path,"开始解析","*"*10)
        data: list = list()
        # lock.acquire()
        ocr = paddleOcrPoll.acquire()
        try:
            result = ocr.ocr(img_path, cls=True)
            for idx in range(len(result)):
                res = result[idx]
                for line in res:
                    data.append(line)
        except Exception as e:
            log.error(e)
        finally:
            # 释放锁
            # lock.release()
            paddleOcrPoll.release(ocr)
            pass
        return img_path,data


    # @utils.calc_self_time
    async def parserImage(self,files) -> dict:
        loop = asyncio.get_running_loop()
        tasks = [loop.run_in_executor(ThreadPool, self.image_ocr, file) for file in files]
        image_data = await asyncio.gather(*tasks)
        results = {}
        for image in image_data:
            strs = []
            filename, data = await image
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
        tasks = [loop.create_task(self.__process_files(files=i)) for i in utils.split_array(files, 4)]
        wait_coro = asyncio.wait(tasks)
        loop.run_until_complete(wait_coro)
        data = {}
        for i in range(len(tasks)):
            data.update(tasks[i].result())
        return data
