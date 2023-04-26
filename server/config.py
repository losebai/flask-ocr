import os
import logging
from concurrent.futures import ThreadPoolExecutor

base_dir = os.getcwd() 

folder_name = "\\files"
config_path = base_dir + folder_name

video_folder_path = base_dir +  "\\video"
imag_folder_path = base_dir + "\\imags"

map3_folder_path = f"{base_dir}/mp3"
wav_folder_path = f"{base_dir}/wav"


objectPoolSize = ocrSize = 0
asrPollSize  = 1
ttsPollSize = 1
ThreadSize = 4

ThreadPool = ThreadPoolExecutor(max_workers=ThreadSize)


# 设置日志级别为DEBUG
logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger("main")
logger.setLevel(logging.DEBUG)

if not os.path.exists(config_path):
    os.makedirs(config_path, exist_ok=True)
if not os.path.exists(video_folder_path):
    os.makedirs(video_folder_path, exist_ok=True)
if not os.path.exists(imag_folder_path):
    os.makedirs(imag_folder_path, exist_ok=True)

if not os.path.exists(map3_folder_path):
    os.makedirs(map3_folder_path, exist_ok=True)
if not os.path.exists(wav_folder_path):
    os.makedirs(wav_folder_path, exist_ok=True)




