from flask import Blueprint, request, jsonify, session
from pymongo import MongoClient
from datetime import datetime

client = MongoClient("mongodb://localhost:27017/")
model_bp = Blueprint("model", __name__, url_prefix="/models")

@model_bp.route("/save", methods=["POST"])
def save_model():
    data = request.json
    required = ["model_name", "framework", "origin_model", "hyperparameters"]
    if not all(field in data for field in required):
        return jsonify({"status": "error", "message": "Missing fields"}), 400

    project = session.get("active_project")
    if not project:
        return jsonify({"status": "error", "message": "No active project"}), 400

    db = client[project]
    models_col = db["models"]

    # check if same model_name exists
    if models_col.find_one({"model_name": data["model_name"]}):
        return jsonify({"status": "error", "message": "Model name already exists"}), 400

    model_doc = {
        "model_name": data["model_name"],
        "framework": data["framework"],
        "origin_model": data["origin_model"],
        "hyperparameters": data["hyperparameters"],
        "created_at": datetime.utcnow()
    }

    models_col.insert_one(model_doc)
    return jsonify({"status": "success"})

@model_bp.route("/list", methods=["GET"])
def list_models():
    project = session.get("active_project")
    if not project:
        return jsonify({"status": "error", "message": "No active project"}), 400

    db = client[project]
    models = list(db["models"].find({}, {"_id": 0}))
    return jsonify(models)

@model_bp.route("/delete", methods=["DELETE"])
def delete_model():
    project = session.get("active_project")
    name = request.args.get("model_name")
    if not project or not name:
        return jsonify({"status": "error", "message": "Missing project or model name"}), 400

    db = client[project]
    result = db["models"].delete_one({"model_name": name})
    if result.deleted_count == 0:
        return jsonify({"status": "error", "message": "Model not found"}), 404

    return jsonify({"status": "success"})
