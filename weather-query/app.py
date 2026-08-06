from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

# uapis 天气查询 API
WEATHER_API_URL = "https://uapis.cn/api/v1/misc/weather"
# 请求超时时间（秒）
TIMEOUT = 10


@app.route("/")
def index():
    """渲染首页"""
    return render_template("index.html")


@app.route("/api/weather")
def get_weather():
    """天气查询接口

    通过 GET 参数 city 传入城市名称，调用 uapis 天气 API，
    返回格式化后的天气信息。对网络错误、城市不存在等异常进行统一处理。
    """
    city = (request.args.get("city") or "").strip()
    if not city:
        return jsonify({"error": "请输入城市名称"}), 400

    # 调用上游天气 API，捕获各类网络异常
    try:
        resp = requests.get(
            WEATHER_API_URL,
            params={"city": city},
            timeout=TIMEOUT,
        )
    except requests.exceptions.Timeout:
        return jsonify({"error": f"查询「{city}」超时，请稍后重试"}), 504
    except requests.exceptions.ConnectionError:
        return jsonify({"error": "网络连接失败，请检查网络后重试"}), 502
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"请求天气服务失败：{e}"}), 500

    # 上游返回 404 表示城市不存在
    if resp.status_code == 404:
        return jsonify({"error": f"未找到城市「{city}」，请确认城市名称"}), 404

    # 其他非 200 状态码统一处理
    if resp.status_code != 200:
        msg = "天气服务暂时不可用"
        try:
            upstream = resp.json()
            if isinstance(upstream, dict) and upstream.get("message"):
                msg = upstream["message"]
        except ValueError:
            pass
        return jsonify({"error": f"天气服务异常（HTTP {resp.status_code}）：{msg}"}), 502

    # 解析响应体
    try:
        data = resp.json()
    except ValueError:
        return jsonify({"error": "天气服务返回数据格式错误"}), 502

    # 二次校验：确认返回了有效天气字段
    if not isinstance(data, dict) or "city" not in data or "weather" not in data:
        return jsonify({"error": f"未找到城市「{city}」的天气信息"}), 404

    return jsonify(data)


if __name__ == "__main__":
    app.run(debug=True, port=5000)
