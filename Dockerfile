FROM python:3.9

ENV PYTHONUNBUFFERED True

ENV APP_HOME /app
WORKDIR $APP_HOME
COPY app.py req.txt ./
COPY static/style.css /app/static/style.css
COPY code_b/angles.py /app/code_b/angles.py
COPY code_b/process_mem.py /app/code_b/process_mem.py

#RUN wget https://storage.googleapis.com/mediapipe-assets/mediapipe/modules/pose_landmark/pose_landmark_heavy.tflite
RUN apt-get update
RUN apt-get install ffmpeg libsm6 libxext6  -y
#RUN pip install --no-cache-dir -r req.txt
RUN pip install -r req.txt
COPY pose_landmark_heavy.tflite ../usr/local/lib/python3.9/site-packages/mediapipe/modules/pose_landmark/pose_landmark_heavy.tflite

EXPOSE 8080

CMD exec gunicorn -b 0.0.0.0:8080 app:server
#CMD python app.py