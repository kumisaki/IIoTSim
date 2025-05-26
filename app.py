from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from pymongo import MongoClient
from datetime import datetime
from utils.data_handler import save_uploaded_file, preview_data

app = Flask(__name__)
CORS(app)

client = MongoClient("mongodb://localhost:27017/")
admin_db = client["IIoTSim_admin"]
projects = admin_db["projects"]

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/get_projects", methods=["GET"])
def get_projects():
    project_list = list(projects.find({}, {"_id": 0, "name": 1}))
    return jsonify([p["name"] for p in project_list])

@app.route("/add_project", methods=["POST"])
def add_project():
    name = request.json.get("name", "").strip()
    if not name:
        return jsonify({"status": "error", "message": "Empty project name"}), 400
    if projects.find_one({"name": name}):
        return jsonify({"status": "error", "message": "Project already exists"}), 400
    projects.insert_one({"name": name, "created_at": datetime.utcnow()})
    sim_db = client[f"sim_{name}"]
    sim_db["metadata"].insert_one({
        "project_name": name,
        "initialized_at": datetime.utcnow()
    })
    return jsonify({"status": "success"})

@app.route("/delete_project", methods=["DELETE"])
def delete_project():
    name = request.json.get("name", "").strip()
    if not name:
        return jsonify({"status": "error", "message": "No project name"}), 400
    result = projects.delete_one({"name": name})
    if result.deleted_count == 0:
        return jsonify({"status": "error", "message": "Project not found"}), 404
    client.drop_database(f"sim_{name}")
    return jsonify({"status": "success"})

@app.route("/upload_data", methods=["POST"])
def upload_data():
    project = request.form.get("project")
    file = request.files.get("file")
    if not project or not file:
        return jsonify({"status": "error", "message": "Missing project or file"}), 400
    filepath = save_uploaded_file(project, file)
    return jsonify({"status": "success", "path": filepath})

@app.route("/preview_data", methods=["GET"])
def preview_project_data():
    project = request.args.get("project")
    if not project:
        return jsonify([])
    data = preview_data(project)
    return jsonify(data or [])

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

if __name__ == "__main__":
    app.run(debug=True)
