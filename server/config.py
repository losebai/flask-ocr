import os
from application import app


folder_name = "\\files"
config_path = os.getcwd() + folder_name


app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 设置上传文件的最大大小为 16MB
app.config['UPLOAD_FOLDER'] = config_path  # 设置上传文件的保存路径
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}  # 设置允许上传的文件扩展名