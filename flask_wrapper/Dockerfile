FROM python:3.10

ENV PYTHONUNBUFFERED True

RUN apt-get update
RUN apt-get upgrade -y
RUN apt-get install ffmpeg libsm6 libxext6  libx264-dev x264 libavcodec-extra libmp3lame-dev libopus-dev libvpx-dev cmake -y

RUN pip install --upgrade pip

#ENV APP_HOME /app
#WORKDIR $APP_HOME
COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY ./assets/*.png /flask_wrapper/assets/
COPY ./assets/*.mp4 /flask_wrapper/assets/
COPY ./assets/robots.txt /flask_wrapper/assets/robots.txt
COPY ./assets/*.svg /flask_wrapper/assets/
COPY ./assets/*.js /flask_wrapper/assets/
COPY ./assets/*.otf /flask_wrapper/assets/
COPY ./assets/*.m4a /flask_wrapper/assets/
COPY ./assets/output.css /flask_wrapper/assets/output.css
COPY ./code_b/*.py /code_b/
COPY ./templates/*.html /flask_wrapper/templates/
COPY ./*.py /flask_wrapper/

COPY /assets/pose_landmark_heavy.tflite ../usr/local/lib/python3.10/site-packages/mediapipe/modules/pose_landmark/pose_landmark_heavy.tflite

EXPOSE 8080

CMD exec gunicorn -b 0.0.0.0:8080 --workers 3 --threads 8 --timeout 0 flask_wrapper.wsgi:app