import os
from . import  config
import uuid
import requests
import asyncio 
import httpx
import cv2
from . import utils
config_path = config.video_folder_path

loop = asyncio.get_event_loop()


hd = {
    'Connection':'keep-alive',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36 SE 2.X MetaSr 1.0'
}


@utils.calc_time
def Download_video(url):
    # 视频网址
    r = requests.get(url, headers=hd, stream=True)
    file_name = url.split("/")[1]
    path = config_path + "\\V_" + f'{file_name}.mp4'
    # with open(path, "wb") as mp4:
    #     for chunk in r.iter_content(chunk_size=1024 * 1024*5):
    #         if chunk:
    #             mp4.write(chunk)
    response = requests.get(url)
    with open(path, 'wb') as f:
        f.write(response.content)
    return path

async def split_video_to_frames(video_path, output_folder = config.imag_folder_path, fps=1, duration=10, frame_size=5):

    cap = cv2.VideoCapture(video_path)
    # 每秒帧率
    frame_rate = cap.get(cv2.CAP_PROP_FPS)
    #总帧率
    total_frames = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    # 基于持续和秒帧率，目标帧率
    target_frame_count = int(duration * frame_rate)
    # 每秒提取的
    frames_per_second =  int(frame_rate / fps)
    current_frame_idx = 0
    frame_count = 0
    frame_files = []

    try:
        fileName = uuid.uuid1()
        while frame_count < target_frame_count:
            ret, frame = await asyncio.to_thread(cap.read)
            if not ret and frame_count == frame_size :
                break

            if frame_count % frames_per_second == 0:
                output_file = os.path.join(output_folder, f"{fileName}_{current_frame_idx}.jpg")
                await asyncio.to_thread(cv2.imwrite, output_file, frame)
                frame_files.append(output_file)
                current_frame_idx += 1
            frame_count += 1
    except Exception as e:
        print(e)

    cap.release()
    return frame_files


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
    headers = {"Range": f"bytes={s_pos}-{e_pos}",'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36 SE 2.X MetaSr 1.0'}
    client = httpx.AsyncClient()
    res = await client.get(url, headers=headers)
    with open(save_name, "rb+") as f:
        f.seek(s_pos)
        f.write(res.content)


@utils.calc_time
def async_download_video(url):
    res = httpx.head(url,verify=False,headers=hd)
    filesize = int(res.headers['Content-Length'])
    divisional_ranges = calc_divisional_range(filesize, 30)
    video_name = uuid.uuid1()
    path = config_path + "\\V_" + f"{video_name}.mp4"
    # 先创建空文件
    with open(path, "wb") as f:
        f.close()

    tasks = [loop.create_task(async_range_download(url,path, s_pos, e_pos))
            for s_pos, e_pos in divisional_ranges]
    # 等待所有协程执行完毕
    loop.run_until_complete(asyncio.wait(tasks))
    return path



from concurrent.futures import ThreadPoolExecutor, as_completed


# 下载方法
def range_download(url,save_name, s_pos, e_pos):
    headers = {"Range": f"bytes={s_pos}-{e_pos}"}
    res = requests.get(url, headers=headers, stream=True,verify=False)
    with open(save_name, "rb+") as f:
        f.seek(s_pos)
        for chunk in res.iter_content(chunk_size=64*1024):
            if chunk:
                f.write(chunk)

@utils.calc_time
def thread_download_video(url):
    res = requests.head(url,verify=False,headers=hd)
    filesize = int(res.headers['Content-Length'])
    divisional_ranges = calc_divisional_range(filesize)


    save_name = "多线程流式下载.mp4"
    # 先创建空文件
    with open(save_name, "wb") as f:
        pass
    with ThreadPoolExecutor() as p:
        futures = []
        for s_pos, e_pos in divisional_ranges:
            print(s_pos, e_pos)
            futures.append(p.submit(range_download,url, save_name, s_pos, e_pos))
        # 等待所有任务执行完毕
        as_completed(futures)

# async_download_video("http://v.ftcdn.net/05/92/31/58/700_F_592315857_VievUFhJXSxENE37GJQjOkirPGE7eFex_ST.mp4")

# async_download_video("https://v99-default.douyinvod.com/02658c04176494b68c50f64fe0af9b2b/644528b3/video/tos/cn/tos-cn-ve-15/oYKCVB8bmlIH8BAwQfFA7TwnADeBEAn7BfpwoH/?a=1128&ch=0&cr=0&dr=0&er=0&cd=0%7C0%7C0%7C0&cv=1&br=1139&bt=1139&cs=0&ds=6&ft=raapL0071gOvGbhBH6xRfUdwU4BO5sKWjjdz7tG&mime_type=video_mp4&qs=0&rc=Nmk0OGhlaWhlNDVlZ2g1O0BpM3J4OmY6Znk4aTMzNGkzM0BjYzM2YGJfX2MxNjFgYTI1YSMtLmstcjQwYzZgLS1kLS9zcw%3D%3D&l=20230423191700C698877CB566231014F1&btag=b8001")