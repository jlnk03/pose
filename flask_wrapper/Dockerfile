FROM python:3.10

ENV PYTHONUNBUFFERED True

#ENV APP_HOME /app
#WORKDIR $APP_HOME
COPY requirements.txt ./
COPY ./*.py /flask_wrapper/
COPY ./templates/*.html /flask_wrapper/templates/
COPY ./assets/*.png /flask_wrapper/assets/
COPY ./assets/*.mp4 /flask_wrapper/assets/
COPY ./assets/output.css /flask_wrapper/assets/output.css
COPY ./assets/robots.txt /flask_wrapper/assets/robots.txt
COPY ./assets/*.svg /flask_wrapper/assets/
COPY ./assets/*.js /flask_wrapper/assets/
COPY ./assets/*.otf /flask_wrapper/assets/
COPY ./code_b/angles.py /code_b/angles.py
COPY ./code_b/process_mem.py /code_b/process_mem.py

RUN apt-get update
RUN apt-get upgrade -y
RUN apt-get install ffmpeg libsm6 libxext6  libx264-dev x264 libfdk-aac-dev libmp3lame-dev libopus-dev libvpx-dev -y

RUN pip install --upgrade pip

RUN pip install --no-cache-dir -r requirements.txt

#COPY /assets/pose_landmark_heavy.tflite ../usr/local/lib/python3.9/site-packages/mediapipe/modules/pose_landmark/pose_landmark_heavy.tflite

EXPOSE 8080

CMD exec gunicorn -b 0.0.0.0:8080 --workers 3 --threads 8 --timeout 0 flask_wrapper.wsgi:app