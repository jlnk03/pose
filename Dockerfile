FROM python:3.9

ENV PYTHONUNBUFFERED True

#ENV APP_HOME /app
#WORKDIR $APP_HOME
#COPY app.py requirements.txt assets./
#COPY assets/style.css /app/assets/style.css
COPY requirements.txt ./
COPY flask_wrapper/*.py /flask_wrapper/
COPY flask_wrapper/templates/*.html /flask_wrapper/templates/
COPY flask_wrapper/assets/background.png /flask_wrapper/assets/background.png
COPY flask_wrapper/assets/output.css /flask_wrapper/assets/output.css
COPY flask_wrapper/assets/graph_amber.svg /flask_wrapper/assets/graph_amber.svg
COPY code_b/angles.py /code_b/angles.py
COPY code_b/process_mem.py /code_b/process_mem.py

RUN apt-get update
RUN apt-get install ffmpeg libsm6 libxext6  -y
RUN pip install --no-cache-dir -r requirements.txt
#RUN pip install -r requirements.txt
COPY flask_wrapper/assets/pose_landmark_heavy.tflite ../usr/local/lib/python3.9/site-packages/mediapipe/modules/pose_landmark/pose_landmark_heavy.tflite

EXPOSE 8080

CMD exec gunicorn -b 0.0.0.0:8080 --workers 3 --threads 8 --timeout 0 flask_wrapper.wsgi:app
#CMD ls
#CMD cd flask_wrapper
#CMD ls
#CMD python -m flask_wrapper.wsgi