import cv2
import os
from . import  config
import uuid
import requests
import asyncio 
import httpx
import requests

import nest_asyncio

hd = {
    'Connection':'keep-alive',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36 SE 2.X MetaSr 1.0'
}

def Download_video(url):
    # 视频网址
    r = requests.get(url, headers=hd, stream=True)
    file_name = url.split("/")[1]
    path = config.config_path + "\\V_" + f'{file_name}.mp4'
    # with open(path, "wb") as mp4:
    #     for chunk in r.iter_content(chunk_size=1024 * 1024*5):
    #         if chunk:
    #             mp4.write(chunk)
    response = requests.get(url)
    with open(path, 'wb') as f:
        f.write(response.content)
    return path

async def imwrite(output_file, frame):
    cv2.imwrite(output_file, frame)


def split_video_to_frames(video_path, output_folder=config.config_path + "video_image", fps=1, duration=10):
    
    if not  os.path.exists(output_folder) and not os.path.isdir(output_folder):
        os.makedirs(output_folder)

    # 打开视频文件
    cap = cv2.VideoCapture(video_path)

    # 获取视频帧率和总帧数
    frame_rate = cap.get(cv2.CAP_PROP_FPS)
    total_frames = cap.get(cv2.CAP_PROP_FRAME_COUNT)

     # 计算要读取的帧数
    target_frame_count = int(duration * frame_rate)

    # 设置每秒获取的帧数
    frames_per_second = int(frame_rate / fps)

    # 逐帧读取视频，保存为图片
    current_frame_idx = 0
    frame_count = 0
    frame_files = []
    try:
        fileName = uuid.uuid1()
        while frame_count < target_frame_count:
            ret, frame = cap.read()
            if not ret and frame_count == 5:
                break

            # 每隔指定帧数保存一张图片
            if frame_count % frames_per_second == 0:
                output_file = os.path.join(output_folder, f"{fileName}_{current_frame_idx}.jpg")
                imwrite(output_file, frame)
                frame_files.append(output_file)
                current_frame_idx += 1
            frame_count += 1
    except Exception as e:
        print(e)

    # 关闭视频文件
    cap.release()

    return frame_files

# split_video_to_frames(r"..\files\test.mp4")


nest_asyncio.apply()


def calc_divisional_range(filesize, chuck=10):
    step = filesize//chuck
    arr = list(range(0, filesize, step))
    result = []
    for i in range(len(arr)-1):
        s_pos, e_pos = arr[i], arr[i+1]-1
        result.append([s_pos, e_pos])
    result[-1][-1] = filesize-1
    return result


# 下载方法
async def async_range_download(url, save_name, s_pos, e_pos):
    headers = {"Range": f"bytes={s_pos}-{e_pos}"}
    res = await client.get(url, headers=headers)
    with open(save_name, "rb+") as f:
        f.seek(s_pos)
        f.write(res.content)

client = httpx.AsyncClient()



def async_download_video(url):
    res = httpx.head(url)
    filesize = int(res.headers['Content-Length'])
    divisional_ranges = calc_divisional_range(filesize, 20)

    video_name = uuid.uuid1()
    path = config.config_path + "\\V_" + f"{video_name}.mp4"
    # 先创建空文件
    with open(path, "wb") as f:
        f.close()

    loop = asyncio.get_event_loop()
    tasks = [async_range_download(video_name, s_pos, e_pos)
            for s_pos, e_pos in divisional_ranges]
    # 等待所有协程执行完毕
    loop.run_until_complete(asyncio.wait(tasks))
    return path

