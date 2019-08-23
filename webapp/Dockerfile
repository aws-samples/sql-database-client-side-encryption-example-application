#https://github.com/GoogleContainerTools/distroless/issues/171
FROM python:3.5-jessie AS build-env

RUN mkdir /app
WORKDIR /app
ADD requirements.txt /app
RUN pip3 install pip==19.1.1
RUN pip3 install -r requirements.txt
ADD app/ /app

FROM gcr.io/distroless/python3
COPY --from=build-env /app /app
COPY --from=build-env /usr/local/lib/python3.5/site-packages /usr/local/lib/python3.5/site-packages

WORKDIR /app
ENV PYTHONPATH=/usr/local/lib/python3.5/site-packages
CMD ["execute.py"]
