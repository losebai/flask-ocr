import os
import logging
from concurrent.futures import ThreadPoolExecutor


folder_name = "\\files"
config_path = os.getcwd() + folder_name

video_folder_path = os.getcwd() +  "\\video"
imag_folder_path = os.getcwd() + "\\imags"

objectPoolSize = 10

ThreadSize = 10
ThreadPool = ThreadPoolExecutor(max_workers=ThreadSize)

logger = logging.getLogger("main")
logger.setLevel(logging.DEBUG)

if not os.path.exists(config_path):
    os.makedirs(config_path, exist_ok=True)
if not os.path.exists(video_folder_path):
    os.makedirs(video_folder_path, exist_ok=True)
if not os.path.exists(imag_folder_path):
    os.makedirs(imag_folder_path, exist_ok=True)

