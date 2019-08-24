FROM ubuntu:latest
RUN apt-get update -qq
RUN apt-get install -y -qq python3 python3-dev python3-pip default-libmysqlclient-dev

RUN mkdir /app
WORKDIR /app
ADD requirements.txt /app
RUN pip3 install pip==19.2.2
RUN pip3 install -r requirements.txt
ADD app/ /app


CMD ["python3","execute.py"]
