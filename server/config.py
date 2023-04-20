import os
import logging
from concurrent.futures import ThreadPoolExecutor

ThreadPool = ThreadPoolExecutor(max_workers=4)

folder_name = "\\wx_tool\\files"
config_path = os.getcwd() + folder_name

video_folder_path = os.getcwd() +  "\\wx_tool\\video"
imag_folder_path = os.getcwd() + "\\wx_tool\\imags"

objectPoolSize = 1

ThreadSize = 10

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

