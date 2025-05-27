from flask import Blueprint, request, jsonify
from pymongo import MongoClient
from datetime import datetime

client = MongoClient("mongodb://localhost:27017/")

device_bp = Blueprint("device", __name__, url_prefix="/devices")


@device_bp.route("/save", methods=["POST"])
def save_device():
    data = request.json
    required_fields = ["project", "device_id", "label", "device_type", "protocol", "model"]
    if not all(field in data for field in required_fields):
        return jsonify({"status": "error", "message": "Missing fields"}), 400

    db = client[f"sim_{data['project']}"]
    devices = db["devices"]

    if devices.find_one({"device_id": data["device_id"]}):
        return jsonify({"status": "error", "message": "Device ID already exists"}), 400

    device_doc = {
        "device_id": data["device_id"],
        "label": data["label"],
        "device_type": data["device_type"],
        "protocol": data["protocol"],
        "model": data["model"],
        "created_at": datetime.utcnow()
    }

    devices.insert_one(device_doc)
    return jsonify({"status": "success"})


@device_bp.route("/list", methods=["GET"])
def list_devices():
    project = request.args.get("project")
    if not project:
        return jsonify({"status": "error", "message": "Missing project name"}), 400

    db = client[f"sim_{project}"]
    device_list = list(db["devices"].find({}, {"_id": 0}))
    return jsonify(device_list)


@device_bp.route("/delete", methods=["DELETE"])
def delete_device():
    project = request.args.get("project")
    device_id = request.args.get("device_id")
    if not project or not device_id:
        return jsonify({"status": "error", "message": "Missing project or device_id"}), 400

    db = client[f"sim_{project}"]
    result = db["devices"].delete_one({"device_id": device_id})
    if result.deleted_count == 0:
        return jsonify({"status": "error", "message": "Device not found"}), 404

    return jsonify({"status": "success"})
