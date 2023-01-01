FROM python:3.9

#ENV PYTHONUNBUFFERED True

ENV APP_HOME /app
WORKDIR $APP_HOME
COPY app.py req.txt ./
COPY static/style.css /app/static/style.css

#RUN wget https://storage.googleapis.com/mediapipe-assets/mediapipe/modules/pose_landmark/pose_landmark_heavy.tflite
RUN apt-get update
RUN apt-get install ffmpeg libsm6 libxext6  -y
RUN pip install --no-cache-dir -r req.txt
COPY pose_landmark_heavy.tflite ../usr/local/lib/python3.9/site-packages/mediapipe/modules/pose_landmark/pose_landmark_heavy.tflite

EXPOSE 8080

#CMD exec gunicorn --bind :8080 --workers 1 --threads 8 --timeout 0 app:server
CMD python app.py