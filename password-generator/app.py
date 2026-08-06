"""密码生成器 Web 应用后端。"""

import secrets
import string

from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

# 字符集定义
CHARACTER_SETS = {
    "lowercase": string.ascii_lowercase,
    "uppercase": string.ascii_uppercase,
    "digits": string.digits,
    "special": "!@#$%^&*()-_=+[]{}|;:,.<>?/~",
}

# 安全限制
MAX_LENGTH = 128
MAX_COUNT = 100


def generate_password(length: int, char_types: list[str]) -> str:
    """根据长度和字符类型生成一个随机密码。

    使用 secrets 模块保证密码学安全的随机性。
    确保每种选中的字符类型至少出现一次。
    """
    if not char_types:
        raise ValueError("至少需要选择一种字符类型")

    # 合并所有可用字符
    pool = "".join(CHARACTER_SETS[ct] for ct in char_types if ct in CHARACTER_SETS)
    if not pool:
        raise ValueError("无效的字符类型")

    # 保证每种选中的字符类型至少出现一次
    password_chars = [
        secrets.choice(CHARACTER_SETS[ct]) for ct in char_types if ct in CHARACTER_SETS
    ]

    # 填充剩余长度
    remaining = length - len(password_chars)
    if remaining > 0:
        password_chars.extend(secrets.choice(pool) for _ in range(remaining))

    # 打乱顺序避免前几位总是固定类型
    secure_rng = secrets.SystemRandom()
    secure_rng.shuffle(password_chars)

    return "".join(password_chars)


@app.route("/")
def index():
    """渲染主页面。"""
    return render_template("index.html")


@app.route("/generate", methods=["POST"])
def generate():
    """批量生成密码的 API 接口。

    请求参数 (JSON):
        length: 密码长度 (4-128)
        char_types: 字符类型列表 ["lowercase", "uppercase", "digits", "special"]
        count: 生成密码数量 (1-100)

    返回:
        JSON 格式的密码列表
    """
    data = request.get_json(silent=True) or {}

    # 参数解析与校验
    try:
        length = int(data.get("length", 16))
    except (TypeError, ValueError):
        return jsonify({"error": "密码长度必须是整数"}), 400

    char_types = data.get("char_types", ["lowercase", "uppercase", "digits"])
    if not isinstance(char_types, list) or not char_types:
        return jsonify({"error": "至少需要选择一种字符类型"}), 400

    try:
        count = int(data.get("count", 1))
    except (TypeError, ValueError):
        return jsonify({"error": "生成数量必须是整数"}), 400

    # 范围校验
    if length < 4 or length > MAX_LENGTH:
        return jsonify({"error": f"密码长度需在 4-{MAX_LENGTH} 之间"}), 400

    if count < 1 or count > MAX_COUNT:
        return jsonify({"error": f"生成数量需在 1-{MAX_COUNT} 之间"}), 400

    invalid_types = [ct for ct in char_types if ct not in CHARACTER_SETS]
    if invalid_types:
        return jsonify({"error": f"无效的字符类型: {invalid_types}"}), 400

    # 生成密码
    try:
        passwords = [generate_password(length, char_types) for _ in range(count)]
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    return jsonify({"passwords": passwords, "count": len(passwords)})


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
