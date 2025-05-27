from flask import Blueprint, request, jsonify
from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
setting_col = client["IIoTSim_admin"]["setting"]

setting_bp = Blueprint("setting", __name__, url_prefix="/setting")

setting_ID = "global_setting"

# ---------- Utility ----------

def get_or_init_setting():
    doc = setting_col.find_one({"_id": setting_ID})
    if not doc:
        default = {"_id": setting_ID, "protocols": [], "frameworks": []}
        setting_col.insert_one(default)
        return default
    return doc

def update_field_array(field, items):
    setting_col.update_one({"_id": setting_ID}, {"$set": {field: items}}, upsert=True)

# ---------- Routes ----------

@setting_bp.route("/get", methods=["GET"])
def get_setting():
    doc = get_or_init_setting()
    return jsonify({
        "protocols": doc.get("protocols", []),
        "frameworks": doc.get("frameworks", [])
    })


@setting_bp.route("/add", methods=["POST"])
def add_setting_item():
    data = request.json
    field = data.get("field")
    value = data.get("value")
    if field not in ["protocols", "frameworks"] or not value:
        return jsonify({"status": "error", "message": "Invalid field or value"}), 400

    doc = get_or_init_setting()
    items = doc.get(field, [])
    if value not in items:
        items.append(value)
        update_field_array(field, items)
    return jsonify({"status": "success"})


@setting_bp.route("/delete", methods=["DELETE"])
def delete_setting_item():
    data = request.json
    field = data.get("field")
    value = data.get("value")
    if field not in ["protocols", "frameworks"] or not value:
        return jsonify({"status": "error", "message": "Invalid field or value"}), 400

    doc = get_or_init_setting()
    items = doc.get(field, [])
    if value in items:
        items.remove(value)
        update_field_array(field, items)
    return jsonify({"status": "success"})
