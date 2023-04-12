from flask import Flask, request,g
from .PaddleOCRUtilService import PaddleOCRUtil,PaddleOCRService
from . import config
from . import utils

import os
os.environ["KMP_DUPLICATE_LIB_OK"]="TRUE"
app = Flask(__name__)


path = config.config_path


if not  os.path.exists(path) and not os.path.isdir(path):
    os.makedirs(path)



#预解析
# PaddleOCRService()
def get_singleton():
    if not hasattr(g, '_singleton_PaddleOCRService'):
        g._singleton = PaddleOCRService(PaddleOCRUtil())
    return g._singleton


@app.route("/parser",methods=["POST"])
@utils.calc_time
def parser() -> dict:
    files = request.files.getlist('file')
    return get_singleton().parserImage_run(files)


def run():
    app.run(threaded=True,debug=False,host='192.168.3.57',port=8888)

