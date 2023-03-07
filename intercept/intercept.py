import hashlib

from flask import Flask, request


def create_app():
    app = Flask(__name__)
    return app


app = create_app()


@app.post("/knowbase")
def knowbase():
    data = request.json()
    filename = f'data/{data["title"]}_{hashlib.md5(data["url"].encode("utf-8")).hexdigest()}.html'
    with open(filename, "w") as f:
        f.write(data["html"])


if __name__ == "__main__":
    app.run(host="localhost", port="8888")
