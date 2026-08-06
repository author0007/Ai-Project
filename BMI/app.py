from flask import Flask, render_template, request, jsonify

app = Flask(__name__)


def calculate_bmi(height_cm, weight_kg):
    """计算BMI值"""
    height_m = height_cm / 100
    bmi = weight_kg / (height_m ** 2)
    return round(bmi, 1)


def get_bmi_category(bmi):
    """根据BMI值返回健康分类和建议"""
    if bmi < 18.5:
        category = "偏瘦"
        advice = {
            "status": "体重偏低",
            "color": "#3498db",
            "tips": [
                "建议适当增加营养摄入，保持均衡饮食",
                "多吃富含蛋白质的食物，如鸡蛋、牛奶、瘦肉等",
                "适量增加主食和健康脂肪的摄入",
                "配合力量训练，增加肌肉量",
                "保证充足睡眠，促进身体发育"
            ]
        }
    elif 18.5 <= bmi < 24:
        category = "正常"
        advice = {
            "status": "体重正常",
            "color": "#27ae60",
            "tips": [
                "恭喜！您的体重在健康范围内",
                "继续保持均衡的饮食习惯",
                "坚持适量运动，每周至少150分钟有氧运动",
                "定期检查身体指标，保持健康生活方式",
                "注意作息规律，避免熬夜"
            ]
        }
    elif 24 <= bmi < 28:
        category = "偏胖"
        advice = {
            "status": "体重偏高",
            "color": "#f39c12",
            "tips": [
                "建议控制热量摄入，避免高油高糖食物",
                "多吃蔬菜水果，增加膳食纤维摄入",
                "减少精米白面，适当增加粗粮",
                "坚持有氧运动，如快走、慢跑、游泳等",
                "每周减重目标建议为0.5-1kg"
            ]
        }
    else:
        category = "肥胖"
        advice = {
            "status": "体重过高",
            "color": "#e74c3c",
            "tips": [
                "建议咨询医生或营养师制定减重计划",
                "严格控制热量摄入，减少高脂肪高糖食物",
                "每日三餐定时定量，避免暴饮暴食",
                "循序渐进增加运动量，从轻度运动开始",
                "定期监测体重和身体指标",
                "必要时进行医学检查，关注身体健康"
            ]
        }
    return category, advice


@app.route("/")
def index():
    """渲染首页"""
    return render_template("index.html")


@app.route("/api/calculate", methods=["POST"])
def calculate():
    """BMI计算API"""
    data = request.get_json()
    height = data.get("height")
    weight = data.get("weight")

    if height is None or weight is None:
        return jsonify({"error": "请提供身高和体重"}), 400

    try:
        height = float(height)
        weight = float(weight)
    except (ValueError, TypeError):
        return jsonify({"error": "身高和体重必须是数字"}), 400

    if height <= 0 or weight <= 0:
        return jsonify({"error": "身高和体重必须大于0"}), 400

    if height < 50 or height > 250:
        return jsonify({"error": "身高请输入合理范围（50-250cm）"}), 400

    if weight < 10 or weight > 500:
        return jsonify({"error": "体重请输入合理范围（10-500kg）"}), 400

    bmi = calculate_bmi(height, weight)
    category, advice = get_bmi_category(bmi)

    return jsonify({
        "bmi": bmi,
        "category": category,
        "advice": advice
    })


if __name__ == "__main__":
    app.run(debug=True, port=5000)
