import django
import os
import uvicorn

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cxm_websocket.settings')
django.setup()

if __name__ == '__main__':
    uvicorn.run("cxm_websocket.asgi:application", reload=True, port=8008)
