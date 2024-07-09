FROM python:3.10.12

WORKDIR /usr/src/app
COPY ./requirements.txt .
RUN pip install --use-deprecated=legacy-resolver --no-cache-dir -r requirements.txt
ENV PYTHONPATH .

CMD python

COPY . .

EXPOSE 8008

RUN ["server.py"]
