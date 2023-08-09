from threading import Lock
from time import sleep

import uvicorn
from fastapi import FastAPI

app = FastAPI()


@app.get("/test")
def test():
    try:
        return {}
    finally:
        sleep(5)
        print("test", flush=True)


def main():
    print("Starting client node server", flush=True)
    uvicorn.run(app="test:app", host="0.0.0.0", port=8000, reload=True)


if __name__ == "__main__":
    main()
