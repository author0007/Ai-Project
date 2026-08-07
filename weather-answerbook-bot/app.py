# SDK 使用说明 SDK user guide：https://open.feishu.cn/document/uAjLw4CM/ukTMukTMukTM/server-side-sdk/python--sdk/preparations-before-development

import lark_oapi as lark
from datetime import datetime
import json
import requests
from lark_oapi.api.im.v1 import *

app_id = "xxx"
app_secret = "xxx"

# UAPI 配置
UAPI_BASE_URL = "https://uapis.cn/api/v1"
UAPI_KEY = ""  # 可选，如需要认证请填入你的 API Key

HEADERS = {
    "Content-Type": "application/json"
}
if UAPI_KEY:
    HEADERS["Authorization"] = f"Bearer {UAPI_KEY}"


def send_message(chat_id: str, content: str):
    """发送消息到飞书会话"""
    client = lark.Client.builder() \
        .app_id(app_id) \
        .app_secret(app_secret) \
        .log_level(lark.LogLevel.DEBUG) \
        .build()

    request: CreateMessageRequest = CreateMessageRequest.builder() \
        .receive_id_type("chat_id") \
        .request_body(CreateMessageRequestBody.builder()
            .receive_id(chat_id)
            .msg_type("text")
            .content(json.dumps({"text": content}))
            .build()) \
        .build()

    response: CreateMessageResponse = client.im.v1.message.create(request)

    if not response.success():
        lark.logger.error(
            f"client.im.v1.message.create failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}, resp: \n{json.dumps(json.loads(response.raw.content), indent=4, ensure_ascii=False)}")
        return

    lark.logger.info(lark.JSON.marshal(response.data, indent=4))


def get_weather(city: str) -> dict:
    """调用 UAPI 天气查询接口"""
    url = f"{UAPI_BASE_URL}/misc/weather"
    params = {
        "city": city,
        "extended": "true",
        "forecast": "false",
        "lang": "zh"
    }

    try:
        response = requests.get(url, params=params, headers=HEADERS, timeout=10)
        response.raise_for_status()
        data = response.json()

        if "code" in data and data["code"] not in [200, None]:
            error_msg = data.get("message", "未知错误")
            return {"success": False, "message": f"查询失败: {error_msg}"}

        return {"success": True, "data": data}

    except requests.exceptions.Timeout:
        return {"success": False, "message": "请求超时，请稍后重试"}
    except requests.exceptions.ConnectionError:
        return {"success": False, "message": "网络连接失败，请检查网络"}
    except requests.exceptions.HTTPError as e:
        return {"success": False, "message": f"HTTP错误: {e}"}
    except Exception as e:
        return {"success": False, "message": f"查询异常: {str(e)}"}


def format_weather_info(weather_data: dict) -> str:
    """格式化天气信息输出"""
    if not weather_data.get("success"):
        return weather_data.get("message", "未知错误")

    data = weather_data["data"]
    result = data.get("result", data)  # 兼容不同返回结构

    # 处理可能的嵌套或直接结构
    if "city" not in result and "data" in result:
        result = result["data"]

    lines = []
    lines.append("🌤️ 天气预报")
    lines.append("=" * 20)

    # 基本信息
    city = result.get("city", "")
    province = result.get("province", "")
    district = result.get("district", "")
    location_parts = [p for p in [province, city, district] if p]
    if location_parts:
        lines.append(f"📍 位置: {' '.join(location_parts)}")

    # 天气状况
    weather = result.get("weather", "")
    temperature = result.get("temperature", "")
    feels_like = result.get("feels_like", "")
    if weather:
        lines.append(f"☁️ 天气: {weather}")
    if temperature:
        lines.append(f"🌡️ 温度: {temperature}°C")
    if feels_like:
        lines.append(f"🤒 体感温度: {feels_like}°C")

    # 风力信息
    wind_direction = result.get("wind_direction", "")
    wind_power = result.get("wind_power", "")
    if wind_direction or wind_power:
        wind_info = f"💨 风力: {wind_direction}" if wind_direction else "💨"
        if wind_power:
            wind_info += f" {wind_power}"
        lines.append(wind_info)

    # 湿度
    humidity = result.get("humidity", "")
    if humidity:
        lines.append(f"💧 湿度: {humidity}%")

    # 空气质量
    aqi = result.get("aqi", "")
    aqi_category = result.get("aqi_category", "")
    if aqi:
        aqi_info = f"🏭 空气质量指数: {aqi}"
        if aqi_category:
            aqi_info += f" ({aqi_category})"
        lines.append(aqi_info)

    # 紫外线
    uv = result.get("uv", "")
    if uv:
        lines.append(f"☀️ 紫外线指数: {uv}")

    # 能见度
    visibility = result.get("visibility", "")
    if visibility:
        lines.append(f"👁️ 能见度: {visibility}km")

    # 气压
    pressure = result.get("pressure", "")
    if pressure:
        lines.append(f"🔽 气压: {pressure}hPa")

    # 更新时间
    report_time = result.get("report_time", "")
    if report_time:
        lines.append(f"🕐 更新时间: {report_time}")

    return "\n".join(lines)


def query_weather(cities_text: str) -> str:
    """查询多个城市的天气"""
    # 支持逗号、空格、顿号分隔的多个城市
    cities = [c.strip() for c in cities_text.replace("，", ",").replace("、", ",").split(",") if c.strip()]

    if not cities:
        return "请输入城市名称，例如：1北京,上海"

    results = []
    for city in cities:
        weather_data = get_weather(city)
        formatted = format_weather_info(weather_data)
        results.append(formatted)

    return "\n\n".join(results)


def ask_answerbook(question: str) -> dict:
    """调用 UAPI 答案之书 POST 接口"""
    url = f"{UAPI_BASE_URL}/answerbook/ask"
    payload = {
        "question": question
    }

    try:
        response = requests.post(url, json=payload, headers=HEADERS, timeout=10)
        response.raise_for_status()
        data = response.json()

        if "code" in data and data["code"] not in [200, None]:
            error_msg = data.get("message", "未知错误")
            return {"success": False, "message": f"查询失败: {error_msg}"}

        return {"success": True, "data": data}

    except requests.exceptions.Timeout:
        return {"success": False, "message": "请求超时，请稍后重试"}
    except requests.exceptions.ConnectionError:
        return {"success": False, "message": "网络连接失败，请检查网络"}
    except requests.exceptions.HTTPError as e:
        return {"success": False, "message": f"HTTP错误: {e}"}
    except Exception as e:
        return {"success": False, "message": f"查询异常: {str(e)}"}


def format_answerbook_response(result: dict, question: str) -> str:
    """格式化答案之书回复"""
    if not result.get("success"):
        return f"❌ {result.get('message', '查询失败')}"

    data = result["data"]
    answer = data.get("answer", "")

    lines = []
    lines.append("📖 答案之书")
    lines.append("=" * 20)
    lines.append(f"❓ 问题: {question}")
    lines.append(f"💡 答案: {answer}")
    lines.append("=" * 20)
    lines.append("🤫 仅供娱乐参考哦~")

    return "\n".join(lines)


def do_p2_im_message_receive_v1(data: lark.im.v1.P2ImMessageReceiveV1) -> None:
    print(f'[ do_p2_im_message_receive_v1 access ], data: {lark.JSON.marshal(data, indent=4)}')

    event = data.event
    if not event:
        print('event is empty')
        return

    message = event.message
    if not message:
        print("message is empty")
        return

    sender_id = event.sender.sender_id.open_id
    chat_id = message.chat_id
    content = message.content
    print(f'收到消息 - 发送者: {sender_id}, 会话ID: {chat_id}, 内容: {content}')

    # 解析消息内容
    # 原始内容格式: {"text":"@_user_1 你好呀"}
    try:
        msg_data = json.loads(content)
        text_content = msg_data.get('text', '')
    except json.JSONDecodeError:
        text_content = content

    # 按空格分隔，提取 @机器人 后面的内容
    parts = list(filter(None, text_content.split(' ')))

    # 过滤掉 @_user_1 等提及标记
    user_parts = [p for p in parts if not p.startswith('@')]
    user_message = ' '.join(user_parts) if user_parts else text_content

    if not user_message:
        send_message(chat_id, "请输入消息内容")
        return

    # 根据指令处理
    command = user_message[0]
    command_text = user_message[1:].strip() if len(user_message) > 1 else ""

    if command == "1":
        # 查询天气
        if not command_text:
            send_message(chat_id, "请输入城市名称，例如：1北京,上海,广州")
            return

        response = query_weather(command_text)
        send_message(chat_id, response)

    elif command == "2":
        # 查询答案之书
        if not command_text:
            send_message(chat_id, "请输入你的问题，例如：2我应该接受这份工作吗？")
            return

        result = ask_answerbook(command_text)
        response = format_answerbook_response(result, command_text)
        send_message(chat_id, response)

    else:
        # 非指令消息，显示规则提示
        rule_message = f"""📋 使用规则
━━━━━━━━━━━━━━
1️⃣ 查询天气
   格式: 1+城市名
   示例: 1北京,上海,广州

2️⃣ 查询答案之书
   格式: 2+你的问题
   示例: 2我今天运气如何？

❓ 你的消息: {user_message}"""
        send_message(chat_id, rule_message)


# SDK标准写法
event_handler = lark.EventDispatcherHandler.builder("", "") \
    .register_p2_im_message_receive_v1(do_p2_im_message_receive_v1) \
    .build()


def main():
    cli = lark.ws.Client(app_id, app_secret,
                        event_handler=event_handler, log_level=lark.LogLevel.DEBUG)
    cli.start()


if __name__ == "__main__":
    main()
