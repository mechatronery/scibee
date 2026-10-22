from flask import Flask, send_from_directory

app = Flask(__name__, static_folder="www", static_url_path="")


@app.route("/")
def home():
    return send_from_directory("www", "index.html")


@app.route("/health")
def health():
    return {"status": "ok"}
