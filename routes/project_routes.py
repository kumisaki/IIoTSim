from flask import Blueprint, request, jsonify, session
from pymongo import MongoClient
from datetime import datetime

client = MongoClient("mongodb://localhost:27017/")
admin_db = client["IIoTSim_admin"]
projects = admin_db["projects"]

project_bp = Blueprint("project", __name__, url_prefix="/projects")

# get all project
@project_bp.route("/get", methods=["GET"])
def get_projects():
    project_list = list(projects.find({}, {"_id": 0, "name": 1, "database_name": 1}))
    return jsonify(project_list)

# add project
@project_bp.route("/add", methods=["POST"])
def add_project():
    name = request.json.get("name", "").strip()
    if not name:
        return jsonify({"message": "Empty name"}), 400

    database_name = f"sim_{name}"
    if projects.find_one({"database_name": database_name}):
        return jsonify({"message": "Exists"}), 400

    projects.insert_one({
        "name": name,
        "database_name": database_name,
        "created_at": datetime.utcnow()
    })

    client[database_name]["metadata"].insert_one({
        "project_name": name,
        "initialized_at": datetime.utcnow()
    })

    return jsonify({"status": "ok"})

# delete project
@project_bp.route("/delete", methods=["DELETE"])
def delete_project():
    name = request.json.get("name", "").strip()
    if not name:
        return jsonify({"message": "No name"}), 400

    database_name = f"sim_{name}"
    projects.delete_one({"database_name": database_name})
    client.drop_database(database_name)

    return jsonify({"status": "ok"})

# setup current project（write into session）
@project_bp.route("/set_active", methods=["POST"])
def set_active_project():
    project = request.json.get("project")
    name = request.json.get("name")

    if not project or not name:
        return jsonify({"status": "error", "message": "Missing project or name"}), 400

    session["active_project"] = project
    session["active_project_name"] = name

    return jsonify({"status": "success", "active": project, "name": name})

# get current project
@project_bp.route("/get_active", methods=["GET"])
def get_active_project():
    project = session.get("active_project")
    if not project:
        return jsonify({"status": "error", "message": "No active project set"}), 400
    return jsonify({"status": "success", "project": project})
