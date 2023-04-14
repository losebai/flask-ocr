import cv2
import os

import requests
 
hd = {
    'Connection':'keep-alive',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36 SE 2.X MetaSr 1.0'
}

def Download_video(url):
    # 视频网址
    r = requests.get(url, headers=hd, stream=True)
    file_name = url.split("/")[1]
    with open(f'{file_name}.mp4', "wb") as mp4:
        for chunk in r.iter_content(chunk_size=1024 * 1024*5):
            if chunk:
                mp4.write(chunk)

def split_video_to_frames(video_path, output_folder=".\\video_image", fps=1):
    
    if not  os.path.exists(output_folder) and not os.path.isdir(output_folder):
        os.makedirs(output_folder)

    # 打开视频文件
    cap = cv2.VideoCapture(video_path)

    # 获取视频帧率和总帧数
    frame_rate = cap.get(cv2.CAP_PROP_FPS)
    total_frames = cap.get(cv2.CAP_PROP_FRAME_COUNT)

    # 设置每秒获取的帧数
    frames_per_second = int(frame_rate / fps)

    # 逐帧读取视频，保存为图片
    current_frame_idx = 0
    frame_count = 0
    frame_files = []
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # 每隔指定帧数保存一张图片
        if frame_count % frames_per_second == 0:
            output_file = os.path.join(output_folder, f"frame_{current_frame_idx}.jpg")
            cv2.imwrite(output_file, frame)
            frame_files.append(output_file)
            current_frame_idx += 1

        frame_count += 1

    # 关闭视频文件
    cap.release()

    return frame_files

# split_video_to_frames(r"..\files\test.mp4")


