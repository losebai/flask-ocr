from paddleocr import PaddleOCR
import asyncio
import time
from . import utils
from . import objectPool
from .config import ThreadPool,logger,objectPoolSize

rec_model_dir = ""
cls_model_dir= ""
det = "..\\ocr_model\\ch_ppocr_server_v2.0_det_infer"
rec = "..\\ocr_model\\\ch_ppocr_mobile_v2.0_rec_infer"

def create_new_object() ->PaddleOCR:
    return PaddleOCR(use_angle_cls=True, lang="ch",page_num=1,det=det,rec=rec,use_tensorrt=True,enable_mkldnn=True,show_log=True)

paddleOcrPoll = objectPool.ObjectPool(create_new_object,objectPoolSize)

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
        except Exception as e:
            log.error(e)
        finally:
            # lock.release()
            paddleOcrPoll.release(ocr)
            logger.debug(f"解析{img_path}完成")
        return img_path,data


    # @utils.calc_self_time
    async def parserImage(self,files) -> dict:
        print("parserImage:"+ time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
        loop = asyncio.get_running_loop()
        tasks = [loop.run_in_executor(ThreadPool, self.image_ocr, file) for file in files]
        return tasks
        

class PaddleOCRService(metaclass=utils.Singleton):

    def __init__(self) -> None:
        self.paddleOCRUtil =  PaddleOCRUtil()
    
    async def parserImage_run(self, files) -> dict:
        loop = asyncio.get_event_loop()
        tasks = [loop.create_task(self.paddleOCRUtil.parserImage(files=i)) for i in utils.split_array(files, 10)]
        # tasks = [loop.create_task(self.paddleOCRUtil.parserImage(files))]
        results = {}
        for task in await asyncio.gather(*tasks):
            for image_ocr in  task:
                strs = []
                filename, data = await image_ocr
                for i in data:
                    strs.append(i[1][0])
                results[filename.split("\\")[-1]] = strs
        return results
