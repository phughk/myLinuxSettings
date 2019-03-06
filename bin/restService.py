#!/usr/bin/python3
from flask import Flask, Response

app = Flask(__name__)

@app.route("/")
def index():
    response = Response("Works")
    response.headers["Grip-Hold"] = "stream"
    response.headers["Grip-Channel"] = "test"
    return response


