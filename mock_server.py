"""模拟 API 服务 — 用于演示和验证 AI 测试框架。"""

from flask import Flask, request, jsonify

app = Flask(__name__)

# 模拟数据库
users_db = {}
tokens_db = {}


@app.route("/api/users", methods=["POST"])
def create_user():
    data = request.get_json()
    username = data.get("username")
    if username in users_db:
        return jsonify({"error": "用户已存在"}), 409
    users_db[username] = {
        "username": username,
        "password": data.get("password"),
        "email": data.get("email", ""),
    }
    return jsonify({"message": "用户创建成功", "data": {"username": username}}), 201


@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"message": "缺少必填字段: username 或 password"}), 400

    user = users_db.get(username)
    if not user:
        return jsonify({"message": "用户不存在"}), 404

    if user["password"] != password:
        return jsonify({"message": "密码错误"}), 401

    token = f"token_{username}_abc123"
    tokens_db[token] = username
    return jsonify({"message": "登录成功", "data": {"token": token}}), 200


@app.route("/api/users/profile", methods=["GET"])
def get_profile():
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    username = tokens_db.get(token)
    if not username:
        return jsonify({"message": "未授权，请先登录"}), 401

    user = users_db.get(username)
    return jsonify({
        "data": {
            "username": user["username"],
            "email": user["email"],
        }
    }), 200


@app.route("/api/users/<username>", methods=["DELETE"])
def delete_user(username):
    if username in users_db:
        del users_db[username]
        return jsonify({"message": "用户已删除"}), 200
    return jsonify({"message": "用户不存在"}), 404


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=False)
