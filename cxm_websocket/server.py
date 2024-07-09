import django
django.setup()

import uvicorn


if __name__ == '__main__':
    uvicorn.run("cxm_websocket.asgi:application", reload=True, port=8000)
