import os

import requests  # type: ignore
import yaml  # type: ignore
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

app = Flask(__name__)

PORT = 3333

# Note: Setting CORS to allow chat.openapi.com is required for ChatGPT to access your plugin
CORS(app, origins=[f"http://localhost:{PORT}", "https://chat.openai.com"])

api_url = "https://admin.marketrightside.com/api"


@app.route("/.well-known/ai-plugin.json")
def serve_manifest():
    return send_from_directory(os.path.dirname(__file__), "ai-plugin.json")


@app.route("/.well-known/openapi.yaml")
def serve_openapi_yaml():
    with open(os.path.join(os.path.dirname(__file__), "openapi.yaml")) as f:
        yaml_data = f.read()
    yaml_data = yaml.load(yaml_data, Loader=yaml.FullLoader)
    return jsonify(yaml_data)


@app.route("/openapi.json")
def serve_openapi_json():
    return send_from_directory(os.path.dirname(__file__), "openapi.json")


@app.route("/<path:path>", methods=["GET", "POST"])
def wrapper(path):
    headers = {
        "Content-Type": "application/json",
    }

    url = f"{api_url}/{path}"
    print(f"Forwarding call: {request.method} {path} -> {url}")

    if request.method == "GET":
        response = requests.get(url, headers=headers, params=request.args)
    elif request.method == "POST":
        print(request.headers)
        response = requests.post(url, headers=headers, params=request.args, json=request.json)
    else:
        raise NotImplementedError(f"Method {request.method} not implemented in wrapper for {path=}")
    return response.content


if __name__ == "__main__":
    app.run(port=PORT)
