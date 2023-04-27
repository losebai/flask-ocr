from ffmpy import FFmpeg as mpy # 音频格式转换对象
import os

def mp3_to_wavp(mp3_path, wav_path):
    '''
    文件夹读取函数
    :param mp3_path:
    :param wav_path:
    :return:
    '''
    # 遍历需要转换的MP3文件夹中的MP3文件
    if not os.path.exists(mp3_path):
        return None

    # 调用格式转换函数
    trans_to_wav(mp3_path, wav_path)



def trans_to_wav(mp3_file, wav_folder):
    '''
    格式转换格式
    :param mp3_file:
    :param wav_folder:
    :return:
    '''
    # 格式化文件
    file_fmt = os.path.basename(mp3_file).strip()
    # 获取文件格式
    file_fmt = file_fmt.split('.')[-1]
    # 校验文件格式
    if file_fmt.strip() != 'mp3':
        raise Exception('改文件不是MP3格式，请检查！')
    elif file_fmt.strip() == '':
        raise Exception('文件格式出现异常，请检查！')
    # 创建wav的文件以供转换完成后输出
    wav_file_path = os.path.join(wav_folder)
    wav_file_path = os.path.join(wav_file_path, '{}.{}'.format(
        os.path.basename(mp3_file).strip().split('.')[0], 'wav'
    ))
    # 创建转换时的命令行参数字符串
    cmder = '-f wav -ac 1 -ar 16000'
    # 创建转换器对象
    mpy_obj = mpy(
        inputs={
            mp3_file: None
        },
        outputs={
            wav_file_path: cmder
        }
    )
    mpy_obj.run()
    return wav_file_path


def compress_image(image_path:str)->str:
    paths =  image_path.split(".")
    out_path = paths[-2]+"_temp." + paths[-1]
    cmder = '-vf scale=iw:ih -codec libwebp -lossless 0 -quality 75'
    # 创建转换器对象
    mpy_obj = mpy(
        inputs={
            image_path: None
        },
        outputs={
            out_path: cmder
        }
    )
    mpy_obj.run()
    return out_path

# compress_image("../test.png","../test2.png")