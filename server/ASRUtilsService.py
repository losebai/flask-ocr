from paddlespeech.cli.asr.infer import ASRExecutor
from paddlespeech.cli.tts.infer import TTSExecutor
from . import objectPool
import random,time,base64,os
from . import config

def create_ASRExecutor() ->ASRExecutor:
    return ASRExecutor()

def create_TTSExecutor() ->TTSExecutor:
    return TTSExecutor()

asrPoll = objectPool.ObjectPool(create_ASRExecutor,config.asrPollSize)
ttsPoll = objectPool.ObjectPool(create_TTSExecutor,config.ttsPollSize)


 
# 公共函数，所有接口都能用
def random_string(length=32): # 生成32位随机字符串，为了生成随机文件名    
    string='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    return ''.join(random.choice(string) for i in range(length))
 
# 公共函数，所有接口都能用
def base64_to_audio(audio_base64, folder_name=None):  # 服务器上用folder_name参数，用于在audio_file_path中拼接路径，如f'/home/www/card/{folder_name}/'，不同的folder_name对应不同的识别任务(如身份证识别、营业执照识别)，本地测试不用
    audio_base64 = audio_base64.split(',')[-1]
    audio = base64.b64decode(audio_base64)
    audio_file_name = random_string() + '_' + (str(time.time()).split('.')[0])  # 不带扩展名，因为不知道收到的音频文件的原始扩展名，手机录的不一定是什么格式
    audio_file_path = f'/home/python/speech/{folder_name}/' + audio_file_name
    with open(audio_file_path, 'wb') as f:
        f.write(audio)
    return audio_file_path
 
# 将收到的音频文件转为16k 16 bit 1 channel的wav文件，16k表示16000Hz的采样率，16bit不知道是什么
# 若给paddlespeech传的文件不对，会提示The sample rate of the input file is not 16000.The program will resample the wav file to 16000.If the result does not meet your expectations，Please input the 16k 16 bit 1 channel wav file.所以要提前转换。
def resample_rate(audio_path_input):
    audio_path_output = audio_path_input + '_output' + '.wav'  # 传入的audio_path_input不带扩展名，所以后面直接拼接字符串
    command = f'ffmpeg -y -i {audio_path_input}  -ac 1 -ar 16000  -b:a 16k  {audio_path_output}'  # 这个命令输出的wav文件，格式上和PaddleSpeech在README中给的示例zh.wav(https://paddlespeech.bj.bcebos.com/PaddleAudio/zh.wav，内容是'我认为跑步最重要的就是给我带来了身体健康')一样。from https://blog.csdn.net/Ezerbel/article/details/124393431
    command_result = os.system(command)  # from https://blog.csdn.net/liulanba/article/details/115466783
    assert command_result == 0
    if os.path.exists(audio_path_output):
        return audio_path_output
    elif not os.path.exists(audio_path_output):  # ffmpeg输出的文件不存在，可能是ffmpeg命令没执行完，等1秒(因在虚拟机测试转一个8.46M的MP3需0.48秒)，1秒后若还没有输出文件，说明报错了
        time.sleep(1)
        if os.path.exists(audio_path_output):
            return audio_path_output
        else:
            return None
