from flask import Flask, request,g
from .PaddleOCRUtilService import PaddleOCRUtil,PaddleOCRService
from . import config
from . import utils
from . import video_parser
from  .asyncUtils import AsyncUtils

import os
os.environ["KMP_DUPLICATE_LIB_OK"]="TRUE"

app = Flask(__name__)


path = config.config_path


app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 设置上传文件的最大大小为 16MB
app.config['UPLOAD_FOLDER'] = path  # 设置上传文件的保存路径
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}  # 设置允许上传的文件扩展名


if not  os.path.exists(path) and not os.path.isdir(path):
    os.makedirs(path)

#预解析
# PaddleOCRService()
def get_singleton():
    if not hasattr(g, '_singleton_PaddleOCRService'):
        g._singleton = PaddleOCRService(PaddleOCRUtil())
    return g._singleton


def files_yield(files):
    for file in files:
        filename = file.filename
        yield filename
        file.save(filename)

@app.route("/parser",methods=["POST"])
def parser() -> dict:
    files = request.files.getlist('file')
    return get_singleton().parserImage_run(files_yield(files))

@app.route("/parser_url",methods=["GET"])
def parserUrl(*args, **kwargs) -> dict:
    url = request.args.get("url")
    videoPath =  video_parser.async_download_video(url)
    # videoPath = path +  "\\test.mp4"
    files =  AsyncUtils.run(video_parser.split_video_to_frames(videoPath,duration=30, frame_size=30))
    data = utils.calc_time(get_singleton().parserImage_run)(files)
    try:
        remove = map(lambda x: os.remove(x), files)
        AsyncUtils.to_thread(remove)
        files = None
    except OSError as e:
        print(f"Error deleting file: {e}")
    return data


def run():
    app.run(threaded=True,debug=False,host='192.168.0.248',port=8888)

