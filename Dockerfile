FROM python:3.7.17

ENV APPDIR /usr/src/app
WORKDIR $APPDIR
COPY ./requirements.txt .
RUN pip install --use-deprecated=legacy-resolver --no-cache-dir -r requirements.txt
ENV PYTHONPATH .
ENV DJANGO_SETTINGS_MODULE cxm_websocket.settings

COPY . .

EXPOSE 8000

CMD ["daphne", "cxm_websocket.asgi:application"]
