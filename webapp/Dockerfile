FROM ubuntu:latest
RUN apt-get update -qq
RUN apt install -y -qq software-properties-common build-essential
RUN add-apt-repository -y ppa:deadsnakes/ppa
RUN apt install -y -qq  python3.7 python3.7-dev default-libmysqlclient-dev
RUN apt install -y -qq curl
RUN curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
RUN python3.7 get-pip.py

RUN mkdir /app
WORKDIR /app
ADD requirements.txt /app
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt
ADD app/ /app


CMD ["python3.7","execute.py"]
