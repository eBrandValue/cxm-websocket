FROM python:3.7.17

ENV APPDIR /usr/src/app
WORKDIR $APPDIR
COPY ./requirements.txt .
RUN pip install --use-deprecated=legacy-resolver --no-cache-dir -r requirements.txt
ENV PYTHONPATH .
ENV DJANGO_SETTINGS_MODULE cxm_websocket.settings

COPY . .

RUN apt-get update && apt-get install -y nginx

COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 8000 80

CMD service nginx start && daphne -b 0.0.0.0 -p 8000 cxm_websocket.asgi:application
