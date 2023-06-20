# flask-ocr
基于paddler实现了图片识别，视频识别，语音识别
# 运行方式
python app.py
或者
flask run app
# 部署方式
uwsgi --http :8000 --wsgi-file app.py --callable app
或者
uwsgi --ini uwsgi.ini
