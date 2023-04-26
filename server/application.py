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
        remove = list(map(lambda x: os.remove(x), files))
        AsyncUtils.to_thread(remove)
        files = None
    except OSError as e:
        print(f"Error deleting file: {e}")
    return data



 
# 语音转文字
# 只接受POST方法访问
@app.route("/speechtotext",methods=["POST"])
def speech_to_text():
    audio_file_base64 = request.get_json().get('audio_file_base64')  # 要转为文字的语音文件的base64编码，开头含不含'data:audio/wav;base64,'都行
    audio_file_path = base64_to_audio(audio_file_base64, folder_name='speech_to_text/audio_file')  # 存放收到的原始音频文件
 
    audio_path_output = resample_rate(audio_path_input=audio_file_path)
    if audio_path_output:
        # asr = ASRExecutor()
        result = asr(audio_file=audio_path_output)  # 会在当前代码所在文件夹中产生exp/log文件夹，里面是paddlespeech的日志文件，每一次调用都会生成一个日志文件。记录这点时的版本号是paddlepaddle==2.3.2，paddlespeech==1.2.0。 from https://github.com/PaddlePaddle/PaddleSpeech/issues/1211
        
        os.remove(audio_file_path)  # 识别成功时删除收到的原始音频文件和转换后的音频文件
        os.remove(audio_path_output)
        # try:
        #     shutil.rmtree('')  # 删除文件夹，若文件夹不存在会报错。若需删除日志文件夹，用这个。from https://blog.csdn.net/a1579990149wqh/article/details/124953746
        # except Exception as e:
        #     pass
 
        return result
    else:
        return None
 
# 文字转语音
# 只接受POST方法访问
@app.route("/texttospeech",methods=["POST"])
def text_to_speech():
    text_str = request.get_json().get('text')  # 要转为语音的文字
 
    # tts = TTSExecutor()
    audio_file_name = random_string() + '_' + (str(time.time()).split('.')[0]) + '.wav'
    audio_file_path = '/home/python/speech/text_to_speech/audio_file' + audio_file_name
    tts(text=text_str, output=audio_file_path)  # 输出24k采样率wav格式音频。同speech_to_text()中一样，会在当前代码所在文件夹中产生exp/log文件夹，里面是paddlespeech的日志文件，每一次调用都会生成一个日志文件。
    if os.path.exists(audio_file_path):
        with open(audio_file_path, 'rb') as f:
            base64_str = base64.b64encode(f.read()).decode('utf-8')  # 开头不含'data:audio/wav;base64,'
        
        os.remove(audio_file_path)  # 识别成功时删除转换后的音频文件
        # try:
        #     shutil.rmtree('')  # 删除文件夹，若文件夹不存在会报错。若需删除日志文件夹，用这个。from https://blog.csdn.net/a1579990149wqh/article/details/124953746
        # except Exception as e:
        #     pass
 
        return base64_str
    elif not os.path.exists(audio_file_path):
        return None

        

def run():
    app.run(threaded=True,debug=False,host='0.0.0.0',port=8888)

