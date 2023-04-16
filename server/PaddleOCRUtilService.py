from paddleocr import PaddleOCR
import asyncio
from concurrent.futures import ThreadPoolExecutor
import time
from . import utils
from . import objectPool
from .  import config

rec_model_dir = ""
cls_model_dir= ""
det = "..\\ocr_model\\ch_ppocr_server_v2.0_det_infer"
rec = "..\\ocr_model\\\ch_ppocr_mobile_v2.0_rec_infer"

def create_new_object():
    return PaddleOCR(use_angle_cls=True, lang="ch",page_num=1,det=det,rec=rec,use_tensorrt=True,enable_mkldnn=True)

_objectSize = 1
paddleOcrPoll = objectPool.ObjectPool(create_new_object,_objectSize)

loop = asyncio.get_event_loop()

class PaddleOCRUtil(metaclass=utils.Singleton):
    
    @utils.calc_self_time
    async def image_ocr(self,img_path) -> list:
        print(time.ctime(time.time()),img_path,"开始解析","*"*10)
        data: list = list()
        # lock.acquire()
        ocr = paddleOcrPoll.acquire()
        try:
            result = ocr.ocr(img_path, cls=True)
            for idx in range(len(result)):
                res = result[idx]
                for line in res:
                    data.append(line)
        finally:
            # 释放锁
            # lock.release()
            paddleOcrPoll.release(ocr)
            pass
        return img_path,data




    @utils.calc_self_time
    async def parserImage(self,files) -> dict:
        with ThreadPoolExecutor(max_workers=4) as executor:
            loop = asyncio.get_event_loop()
            tasks = [loop.run_in_executor(executor, self.image_ocr, file) for file in files]
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
       

    def parserImage_run(self, files) -> dict:
        loop = asyncio.get_event_loop()
        tasks = [loop.create_task(self.paddleOCRUtil.parserImage(files=i)) for i in utils.split_array(files, 4)]
        wait_coro = asyncio.wait(tasks)
        loop.run_until_complete(wait_coro)
        data = {}
        for i in range(len(tasks)):
            data.update(tasks[i].result())
        return data

"""
如果希望使用不支持空格的识别模型，在预测的时候需要注意：请将代码更新到最新版本，并添加参数 --use_space_char=False。
如果不希望使用方向分类器，在预测的时候需要注意：请将代码更新到最新版本，并添加参数 --use_angle_cls=False。
"""    