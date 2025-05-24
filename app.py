from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from pymongo import MongoClient
from datetime import datetime

app = Flask(__name__)
CORS(app)  # 允许跨域（前后端分离部署时可用）

# MongoDB 连接配置
client = MongoClient("mongodb://localhost:27017/")
db = client["sensor_sim"]
collection = db["projects"]

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/get_projects", methods=["GET"])
def get_projects():
    admin_db = client["IIoTSim_admin"]
    projects = admin_db["projects"]
    project_list = list(projects.find({}, {"_id": 0, "name": 1}))
    return jsonify([p["name"] for p in project_list])

@app.route("/add_project", methods=["POST"])
def add_project():
    name = request.json.get("name", "").strip()
    if not name:
        return jsonify({"status": "error", "message": "Empty project name"}), 400

    admin_db = client["IIoTSim_admin"]
    projects = admin_db["projects"]

    # 检查是否已存在
    if projects.find_one({"name": name}):
        return jsonify({"status": "error", "message": "Project already exists"}), 400

    # 添加项目记录
    projects.insert_one({
        "name": name,
        "created_at": datetime.utcnow()
    })

    # 创建对应项目数据库（空即可，插入一条 metadata 可选）
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
    result = collection.delete_one({"name": name})
    if result.deleted_count == 0:
        return jsonify({"status": "error", "message": "Project not found"}), 404
    return jsonify({"status": "success"})

if __name__ == "__main__":
    app.run(debug=True)
