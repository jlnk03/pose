FROM python:3.9

ENV PYTHONUNBUFFERED True

ENV APP_HOME /app
WORKDIR $APP_HOME
#COPY app.py requirements.txt assets./
#COPY assets/style.css /app/assets/style.css
COPY flask_wrapper /app/flask_wrapper
COPY code_b/angles.py /app/code_b/angles.py
COPY code_b/process_mem.py /app/code_b/process_mem.py


RUN apt-get update
RUN apt-get install ffmpeg libsm6 libxext6  -y
#RUN pip install --no-cache-dir -r requirements.txt
RUN pip install -r requirements.txt
COPY assets/pose_landmark_heavy.tflite ../usr/local/lib/python3.9/site-packages/mediapipe/modules/pose_landmark/pose_landmark_heavy.tflite

EXPOSE 8080

CMD exec gunicorn -b 0.0.0.0:8080 --workers 3 --threads 8 --timeout 0 app:server
#CMD python app.py