from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

# uapis 答案之书 API（POST 方式）
ANSWERBOOK_API_URL = "https://uapis.cn/api/v1/answerbook/ask"
# 请求超时时间（秒）
TIMEOUT = 15


@app.route("/")
def index():
    """渲染首页"""
    return render_template("index.html")


@app.route("/api/ask", methods=["POST"])
def ask():
    """答案之书问答接口

    通过 POST 表单参数 question 传入问题，调用 uapis 答案之书 API，
    返回问题对应的神秘答案。对网络错误、超时、服务异常等情况进行统一处理。
    """
    # 兼容 JSON / 表单两种提交方式
    if request.is_json:
        question = (request.get_json(silent=True) or {}).get("question", "")
    else:
        question = request.form.get("question", "")
    question = (question or "").strip()

    if not question:
        return jsonify({"error": "请输入你的问题"}), 400

    # 调用上游答案之书 API，捕获各类网络异常
    try:
        resp = requests.post(
            ANSWERBOOK_API_URL,
            data={"question": question},
            timeout=TIMEOUT,
        )
    except requests.exceptions.Timeout:
        return jsonify({"error": f"询问「{question}」超时，请稍后重试"}), 504
    except requests.exceptions.ConnectionError:
        return jsonify({"error": "网络连接失败，请检查网络后重试"}), 502
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"请求答案之书失败：{e}"}), 500

    # 非 200 状态码统一处理
    if resp.status_code != 200:
        msg = "答案之书服务暂时不可用"
        try:
            upstream = resp.json()
            if isinstance(upstream, dict) and upstream.get("message"):
                msg = upstream["message"]
        except ValueError:
            pass
        return jsonify({"error": f"答案之书服务异常（HTTP {resp.status_code}）：{msg}"}), 502

    # 解析响应体
    try:
        data = resp.json()
    except ValueError:
        return jsonify({"error": "答案之书返回数据格式错误"}), 502

    # 二次校验：确认返回了有效答案字段
    if not isinstance(data, dict) or "answer" not in data:
        return jsonify({"error": "答案之书未给出答案，请稍后重试"}), 502

    # 统一返回结构，question 以用户输入为准
    return jsonify({
        "question": question,
        "answer": data.get("answer", ""),
    })


if __name__ == "__main__":
    app.run(debug=True, port=5001)
