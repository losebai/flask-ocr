from flask                                  import Flask, request,g,jsonify
from .PaddleOCRUtilService                  import PaddleOCRService
from .ASRUtilsService                       import ASRService
from .                                      import config
from .                                      import utils
from .                                      import video_parser
from .ffmpUtils                             import compress_image
from .asyncUtils                            import AsyncUtils
from .result                                import Result
from flask_sockets                          import Sockets
from geventwebsocket.handler                import WebSocketHandler
from gevent.pywsgi                          import WSGIServer
from paddlespeech.server.engine.engine_pool import get_engine_pool

import os
import json

os.environ["KMP_DUPLICATE_LIB_OK"]="TRUE"

app = Flask(__name__)
sockets=Sockets(app)

path = config.config_path

logger = config.logger
# server_executor = ServerExecutor()
user_socket_dict={}

app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 设置上传文件的最大大小为 16MB
app.config['UPLOAD_FOLDER'] = path  # 设置上传文件的保存路径
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}  # 设置允许上传的文件扩展名


if not  os.path.exists(path) and not os.path.isdir(path):
    os.makedirs(path)

#预解析
# PaddleOCRService()
def get_singleton():
    if not hasattr(g, '_singleton_PaddleOCRService'):
        g._singleton = PaddleOCRService()
    return g._singleton


def files_yield(files):
    for file in files:
        filename = file.filename
        yield filename
        file.save(filename)

def del_file(files):
    try:
        remove = list(map(lambda x: os.remove(x), files))
        AsyncUtils.to_thread(remove)
        del files
        del remove
    except OSError as e:
        print(f"Error deleting file: {e}")

@utils.calc_time
@app.route("/parser",methods=["POST"])
def parser() -> dict:
    data = request.args
    filePaths = []
    temps = []
    if data.get("type") == '1':
        url = request.args.get("url")
        suf = url.split(".")[-1]
        file_path = video_parser.async_download_video(url,suf=suf)
        temps.append(file_path)
        filePaths.append(compress_image(file_path))
    elif data.get("type") == '2':
        files = request.files.getlist('file')
        filePaths = list(files_yield(files))
    data = utils.calc_time(AsyncUtils.run)(PaddleOCRService().parserImage_run(filePaths))
    del_file(filePaths + temps)
    return data

@utils.calc_time
@app.route("/parser_url",methods=["GET"])
def parserUrl() -> dict:
    url = request.args.get("url")
    videoPath =  video_parser.async_download_video(url)
    # videoPath = path +  "\\test.mp4"
    files = AsyncUtils.run(video_parser.split_video_to_frames(videoPath))
    data = utils.calc_time(AsyncUtils.run)(PaddleOCRService().parserImage_run(files))
    del_file(files)
    return data
 
# 语音转文字
@utils.calc_time
@app.route("/speechtotext",methods=["POST"])
def speech_to_text():
    data = request.args
    audio_base64, audio_file = None, None
    if data.get("type") == '1':
        audio_base64 = request.get_json().get('audio_base64')  # 要转为文字的语音文件的base64编码，开头含不含'data:audio/wav;base64,'都行
    elif data.get("type") == '2':
        file = request.files['file']
        # 将文件保存到本地
        audio_file = f"{path}/{file.filename}"
        file.save(audio_file)
    elif data.get("type") == '3':
        url = data.get("url")
        audio_file =  video_parser.async_download_video(url)
    else:
        return jsonify(Result.error())
    return jsonify(Result.ok(ASRService().speech_to_text(audio_base64,audio_file)))


 
# 文字转语音
# 只接受POST方法访问
@utils.calc_time
@app.route("/texttospeech",methods=["POST"])
def text_to_speech():
    text_str = request.get_json().get('text')  # 要转为语音的文字
    return jsonify(Result.ok(ASRService().text_to_speech(text_str)))



# todo 暂时不可用
@sockets.route('/paddlespeech/asr/streaming/<username>')
def websocket_endpoint(self,username):
    """PaddleSpeech Online ASR Server api

    Args:
        websocket (WebSocket): the websocket instance
    """ 
    user_socket=request.environ.get("wsgi.websocket")
    if not user_socket:
        return "请以WEBSOCKET方式连接"

    user_socket_dict[username]=user_socket
    #1. the interface wait to accept the websocket protocal header
    #   and only we receive the header, it establish the connection with specific thread
    # await websocket.accept()
# 
    #2. if we accept the websocket headers, we will get the online asr engine instance
    engine_pool = get_engine_pool()
    asr_model = engine_pool['asr']

    #3. each websocket connection, we will create an PaddleASRConnectionHanddler to process such audio
    #   and each connection has its own connection instance to process the request
    #   and only if client send the start signal, we create the PaddleASRConnectionHanddler instance
    connection_handler = None

    try:
        #4. we do a loop to process the audio package by package according the protocal
        #   and only if the client send finished signal, we will break the loop
        while True:
            # careful here, changed the source code from starlette.websockets
            # 4.1 we wait for the client signal for the specific action
            message =  user_socket.receive()
            for user_name,u_socket in user_socket_dict.items():
                # websocket._raise_on_disconnect(message)

                #4.2 text for the action command and bytes for pcm data
                if "text" in message:
                    # we first parse the specific command
                    message = json.loads(message["text"])
                    if 'signal' not in message:
                        resp = {"status": "ok", "message": "no valid json data"}
                        u_socket.send(resp)

                    # start command, we create the PaddleASRConnectionHanddler instance to process the audio data
                    # end command, we process the all the last audio pcm and return the final result
                    #              and we break the loop
                    if message['signal'] == 'start':
                        resp = {"status": "ok", "signal": "server_ready"}
                        # do something at begining here
                        # create the instance to process the audio
                        #connection_handler = PaddleASRConnectionHanddler(asr_model)
                        connection_handler = asr_model.new_handler()
                        u_socket.send(resp)
                    elif message['signal'] == 'end':
                        # reset single  engine for an new connection
                        # and we will destroy the connection
                        connection_handler.decode(is_finished=True)
                        connection_handler.rescoring()
                        asr_results = connection_handler.get_result()
                        word_time_stamp = connection_handler.get_word_time_stamp()
                        connection_handler.reset()

                        resp = {
                            "status": "ok",
                            "signal": "finished",
                            'result': asr_results,
                            'times': word_time_stamp
                        }
                        u_socket.send(resp)
                        break
                    else:
                        resp = {"status": "ok", "message": "no valid json data"}
                        u_socket.send(resp)

                elif "bytes" in message:
                    # bytes for the pcm data
                    message = message["bytes"]

                    # we extract the remained audio pcm 
                    # and decode for the result in this package data
                    connection_handler.extract_feat(message)
                    connection_handler.decode(is_finished=False)

                    if connection_handler.endpoint_state:
                        logger.info("endpoint: detected and rescoring.")
                        connection_handler.rescoring()
                        word_time_stamp = connection_handler.get_word_time_stamp()

                    asr_results = connection_handler.get_result()

                    if connection_handler.endpoint_state:
                        if connection_handler.continuous_decoding:
                            logger.info("endpoint: continue decoding")
                            connection_handler.reset_continuous_decoding()
                        else:
                            logger.info("endpoint: exit decoding")
                            # ending by endpoint
                            resp = {
                                "status": "ok",
                                "signal": "finished",
                                'result': asr_results,
                                'times': word_time_stamp
                            }
                            u_socket.send(resp)
                            break

                    # return the current partial result
                    # if the engine create the vad instance, this connection will have many partial results 
                    resp = {'result': asr_results}
                    u_socket.send(resp)

    except Exception as e:
        logger.error(e)
        user_socket_dict.pop(username)



def run():
    app.run(threaded=True,debug=False,host='0.0.0.0',port=5000)
    # http_serve=WSGIServer(("0.0.0.0",5000),app,handler_class=WebSocketHandler)
    # http_serve.serve_forever()