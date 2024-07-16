FROM python:3.10.12

ENV APPDIR /usr/src/app
WORKDIR $APPDIR
COPY ./requirements.txt .
RUN pip install --upgrade pip
RUN pip install --use-deprecated=legacy-resolver --no-cache-dir -r requirements.txt

ENV PYTHONPATH .
ENV DJANGO_SETTINGS_MODULE cxm_websocket.settings

COPY . .

RUN apt-get update && apt-get install -y nginx && apt-get install nano && apt-get install -y certbot python3-certbot-nginx

#COPY nginx2.conf /etc/nginx/sites-available/ws.conf
COPY nginx3.conf /etc/nginx/nginx.conf

EXPOSE 80 443 8000

CMD service nginx start && daphne -b 0.0.0.0 -p 8000 cxm_websocket.asgi:application
