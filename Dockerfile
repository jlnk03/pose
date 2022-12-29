FROM python:3.10

ENV APP_HOME /app
WORKDIR $APP_HOME
COPY . ./

RUN pip install -r requirements.txt
RUN apt-get update && apt-get install libgl1

EXPOSE 8080

CMD python application.py