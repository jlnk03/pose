FROM python:3.9

ENV APP_HOME /app
WORKDIR $APP_HOME
COPY static app.py req.txt ./

RUN apt-get update
RUN apt-get install ffmpeg libsm6 libxext6  -y
RUN pip3 install -r req.txt

EXPOSE 8080

CMD python app.py