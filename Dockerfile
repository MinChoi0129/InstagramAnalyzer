FROM python:3
ENV TZ=Asia/Seoul
WORKDIR /usr/src

RUN pip install flask
RUN pip install bcrypt

COPY app.py /usr/src/
COPY User.py /usr/src/
COPY static /usr/src/static
COPY templates /usr/src/templates

CMD [ "python3", "main.py"]