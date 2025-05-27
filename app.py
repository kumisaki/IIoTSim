from flask import Flask, render_template, session
from flask_cors import CORS
from routes import register_routes

app = Flask(__name__)

app.secret_key = "secret_key"

CORS(app)
register_routes(app)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/devices/list")
def devices_list():
    return render_template("devices_list.html")

@app.route("/devices/edit")
def device_edit():
    return render_template("device_edit.html")

@app.route("/models/list")
def models_list():
    return render_template("models_list.html")

@app.route("/models/edit")
def model_edit():
    return render_template("model_edit.html")

@app.route("/setting")
def configuration():
    return render_template("setting.html")

if __name__ == "__main__":
    app.run(debug=True)
